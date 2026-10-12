import os, time, secrets, hashlib, hmac, re, sqlite3, ssl, smtplib
from email.message import EmailMessage
from http.server import ThreadingHTTPServer
from .common import Handler,db,pw_hash,pw_verify
PORT=int(os.environ.get('IDENTITY_PORT','8101'))
def init():
    with db('identity.sqlite3') as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, display TEXT NOT NULL, practice_id TEXT NOT NULL, role TEXT NOT NULL, password_hash TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1, status TEXT NOT NULL DEFAULT 'approved',email TEXT NOT NULL DEFAULT '',email_verified INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id),expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS consultations(id TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id), chip TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('approved','pending','revoked')));
        CREATE TABLE IF NOT EXISTS password_resets(token_hash TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id),expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS login_challenges(id TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id),code_hash TEXT NOT NULL,expires INTEGER NOT NULL,created INTEGER NOT NULL,attempts INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS email_challenges(id TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id),code_hash TEXT NOT NULL,expires INTEGER NOT NULL,created INTEGER NOT NULL,attempts INTEGER NOT NULL DEFAULT 0);''')
        columns={row['name'] for row in c.execute('PRAGMA table_info(users)')}
        if 'status' not in columns:c.execute("ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'approved'")
        if 'email' not in columns:c.execute("ALTER TABLE users ADD COLUMN email TEXT NOT NULL DEFAULT ''")
        if 'email_verified' not in columns:c.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 0")
        if not c.execute('SELECT 1 FROM users').fetchone():
            demo_pw=os.environ.get('DIERSIGNAAL_DEMO_PASSWORD','PilotDemo!2026')
            demos=[('arts.west','Dr. Noor de Vries','west','veterinarian','DIERSIGNAAL_EMAIL_ARTS_WEST'),
                   ('arts.noord','Dr. Sam Bakker','noord','veterinarian','DIERSIGNAAL_EMAIL_ARTS_NOORD'),
                   ('reviewer','Juridisch beoordelaar','review','auditor','DIERSIGNAAL_EMAIL_REVIEWER')]
            c.executemany("INSERT INTO users(id,display,practice_id,role,password_hash,active,status,email,email_verified) VALUES(?,?,?,?,?,1,'approved',?,?)",
                          [(name,display,practice,role,pw_hash(demo_pw),os.environ.get(email_key,''),int(bool(os.environ.get(email_key,'')))) for name,display,practice,role,email_key in demos])
            c.executemany('INSERT INTO consultations VALUES(?,?,?,?)',[
                ('CONS-W-1001','arts.west','999000000000001','approved'),
                ('CONS-W-1002','arts.west','999000000000002','approved'),
                ('CONS-N-3001','arts.noord','999000000000001','approved'),
                ('CONS-W-9999','arts.west','999000000000003','revoked')])
        admin_password=os.environ.get('DIERSIGNAAL_ADMIN_PASSWORD',os.environ.get('DIERSIGNAAL_DEMO_PASSWORD','PilotDemo!2026'))
        admin_email=os.environ.get('DIERSIGNAAL_ADMIN_EMAIL','')
        c.execute('INSERT OR IGNORE INTO users(id,display,practice_id,role,password_hash,active,status,email,email_verified) VALUES(?,?,?,?,?,1,?,?,?)',
                  ('beheerder','Demo-beheerder','beheer','admin',pw_hash(admin_password),'approved',admin_email,int(bool(admin_email))))
        if admin_email:
            c.execute("UPDATE users SET email=?,email_verified=1 WHERE id='beheerder' AND email=''",(admin_email,))
        for username,email_key in [('arts.west','DIERSIGNAAL_EMAIL_ARTS_WEST'),('arts.noord','DIERSIGNAAL_EMAIL_ARTS_NOORD'),('reviewer','DIERSIGNAAL_EMAIL_REVIEWER')]:
            configured_email=os.environ.get(email_key,'')
            if configured_email:c.execute("UPDATE users SET email=?,email_verified=1 WHERE id=? AND email=''",(configured_email,username))
def digest(token): return hashlib.sha256(token.encode()).hexdigest()
def email_valid(value):
    if len(value)>254 or value.count('@')!=1:return False
    local=value.split('@',1)[0]
    if not local or len(local)>64 or local.startswith('.') or local.endswith('.') or '..' in local:return False
    local_chars=".!#$%&'*+/=?^_`{|}~-"
    if any(not char.isascii() or not (char.isalnum() or char in local_chars) for char in local):return False
    domain=value.split('@',1)[1]
    labels=domain.split('.')
    return len(domain)<=253 and len(labels)>=2 and all(
        0<len(label)<=63 and label[0].isascii() and label[0].isalnum() and label[-1].isascii() and label[-1].isalnum()
        and all(char.isascii() and (char.isalnum() or char=='-') for char in label)
        for label in labels)
def mfa_digest(challenge_id,user_id,code):
    key=os.environ.get('DIERSIGNAAL_MFA_SECRET') or os.environ.get('DIERSIGNAAL_INTERNAL_SECRET','')
    if len(key)<32:raise RuntimeError('MFA challenge secret is not configured')
    return hmac.new(key.encode(),f'{challenge_id}:{user_id}:{code}'.encode(),hashlib.sha256).hexdigest()
def email_code_digest(challenge_id,user_id,code):
    key=os.environ.get('DIERSIGNAAL_MFA_SECRET') or os.environ.get('DIERSIGNAAL_INTERNAL_SECRET','')
    if len(key)<32:raise RuntimeError('MFA challenge secret is not configured')
    return hmac.new(key.encode(),f'email:{challenge_id}:{user_id}:{code}'.encode(),hashlib.sha256).hexdigest()
def send_mfa_email(recipient,code,purpose='login'):
    host=os.environ.get('DIERSIGNAAL_SMTP_HOST','')
    sender=os.environ.get('DIERSIGNAAL_SMTP_FROM','')
    if not host or not email_valid(sender) or not email_valid(recipient):
        raise RuntimeError('Secure email delivery is not configured')
    port=int(os.environ.get('DIERSIGNAAL_SMTP_PORT','465'))
    ca_file=os.environ.get('DIERSIGNAAL_SMTP_CA')
    context=ssl.create_default_context(cafile=ca_file or None)
    message=EmailMessage()
    verifying_email=purpose=='email_verification'
    message['Subject']='Bevestig je DierSignaal-e-mailadres' if verifying_email else 'Je DierSignaal-inlogcode'
    message['From']=sender
    message['To']=recipient
    if verifying_email:
        message.set_content(f'Je eenmalige DierSignaal-e-mailverificatiecode is: {code}\n\nDe code is 15 minuten geldig en kan maximaal vijf keer worden geprobeerd. Deel deze code met niemand.')
    else:
        message.set_content(f'Je eenmalige DierSignaal-inlogcode is: {code}\n\nDe code is 10 minuten geldig en kan maximaal vijf keer worden geprobeerd. Deel deze code met niemand. Heb je niet geprobeerd in te loggen, neem dan contact op met de beheerder.')
    with smtplib.SMTP_SSL(host,port,context=context,timeout=10) as smtp:
        username=os.environ.get('DIERSIGNAAL_SMTP_USER','')
        smtp_credential=os.environ.get('DIERSIGNAAL_SMTP_PASSWORD','')
        if username or smtp_credential:
            if not username or not smtp_credential:raise RuntimeError('Both SMTP username and credential are required')
            smtp.login(username,smtp_credential)
        smtp.send_message(message)
def session(token):
    if not token: return None
    with db('identity.sqlite3') as c:
        row=c.execute('''SELECT u.id,u.display,u.practice_id,u.role FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires>? AND u.active=1 AND u.status='approved' AND u.email_verified=1''',(digest(token),int(time.time()))).fetchone()
        return dict(row) if row else None
class Api(Handler):
    def do_POST(self):
        p=self.route()
        try: data=self.body()
        except Exception: return self.error(400,'Ongeldige JSON')
        if p=='/register':
            name=str(data.get('username','')).strip();display=str(data.get('display','')).strip();practice=str(data.get('practice_id','')).strip();new_secret=str(data.get('password',''));email=str(data.get('email','')).strip()
            if not re.fullmatch(r'[A-Za-z0-9._-]{3,64}',name) or not display or len(display)>100 or not practice or len(practice)>100 or len(new_secret)<12 or len(new_secret)>200 or not email_valid(email):
                return self.error(400,'Controleer gebruikersnaam, praktijk, e-mailadres, naam en wachtwoord (minimaal 12 tekens)')
            with db('identity.sqlite3') as c:
                try:c.execute("INSERT INTO users(id,display,practice_id,role,password_hash,active,status,email,email_verified) VALUES(?,?,?,?,?,0,'pending',?,0)",(name,display,practice,'veterinarian',pw_hash(new_secret),email))
                except sqlite3.IntegrityError:return self.error(409,'Deze gebruikersnaam is al in gebruik')
            return self.send_json(201,{'status':'pending','message':'Registratie ontvangen; beheer moet het account goedkeuren en het e-mailadres bevestigen.'})
        if p=='/email/verify':
            name=str(data.get('username',''))[:64];code=str(data.get('code',''))
            if not re.fullmatch(r'[0-9]{6}',code):return self.error(400,'Verificatiecode ongeldig of verlopen')
            with db('identity.sqlite3') as c:
                row=c.execute("SELECT id,user_id,code_hash,attempts FROM email_challenges WHERE user_id=? AND expires>?",(name,int(time.time()))).fetchone()
                if not row or row['attempts']>=5:return self.error(400,'Verificatiecode ongeldig of verlopen')
                expected=email_code_digest(row['id'],row['user_id'],code)
                if not hmac.compare_digest(row['code_hash'],expected):
                    c.execute('UPDATE email_challenges SET attempts=attempts+1 WHERE id=?',(row['id'],))
                    return self.error(400,'Verificatiecode ongeldig of verlopen')
                c.execute('UPDATE users SET email_verified=1 WHERE id=? AND email<>?',(name,''))
                c.execute('DELETE FROM email_challenges WHERE user_id=?',(name,))
            return self.send_json(200,{'ok':True,'message':'E-mailadres bevestigd. Een beheerder moet het account nog goedkeuren.'})
        if p=='/login/mfa':
            challenge_id=str(data.get('challenge_id',''));code=str(data.get('code',''))
            if not re.fullmatch(r'[0-9]{6}',code):return self.error(401,'Code ongeldig of verlopen')
            with db('identity.sqlite3') as c:
                row=c.execute("""SELECT ch.user_id,ch.code_hash,ch.attempts,u.id,u.display,u.practice_id,u.role
                                 FROM login_challenges ch JOIN users u ON u.id=ch.user_id
                                 WHERE ch.id=? AND ch.expires>? AND u.active=1 AND u.status='approved' AND u.email_verified=1""",
                              (challenge_id,int(time.time()))).fetchone()
                if not row or row['attempts']>=5:return self.error(401,'Code ongeldig of verlopen')
                expected=mfa_digest(challenge_id,row['user_id'],code)
                if not hmac.compare_digest(row['code_hash'],expected):
                    c.execute('UPDATE login_challenges SET attempts=attempts+1 WHERE id=?',(challenge_id,))
                    return self.error(401,'Code ongeldig of verlopen')
                c.execute('DELETE FROM login_challenges WHERE id=?',(challenge_id,))
                token=secrets.token_urlsafe(36)
                c.execute('DELETE FROM sessions WHERE expires<?',(int(time.time()),))
                c.execute('INSERT INTO sessions VALUES(?,?,?)',(digest(token),row['user_id'],int(time.time())+1800))
            return self.send_json(200,{'token':token,'user':{'id':row['id'],'display':row['display'],'role':row['role'],'practice_id':row['practice_id']},'expires_in':1800})
        if p=='/password-reset':
            name=str(data.get('username',''))[:64];code=str(data.get('code',''))[:100];new_secret=str(data.get('password',''))
            if len(new_secret)<12 or len(new_secret)>200:return self.error(400,'Het nieuwe wachtwoord moet minimaal 12 tekens bevatten')
            with db('identity.sqlite3') as c:
                row=c.execute("""SELECT r.token_hash FROM password_resets r JOIN users u ON u.id=r.user_id
                                 WHERE u.id=? AND r.expires>? AND u.status='approved' AND u.active=1""",(name,int(time.time()))).fetchone()
                if not row or not hmac.compare_digest(row['token_hash'],digest(code)):return self.error(400,'Herstelcode ongeldig of verlopen')
                c.execute('UPDATE users SET password_hash=? WHERE id=?',(pw_hash(new_secret),name))
                c.execute('DELETE FROM password_resets WHERE user_id=?',(name,))
                c.execute('DELETE FROM sessions WHERE user_id=?',(name,))
                c.execute('DELETE FROM login_challenges WHERE user_id=?',(name,))
            return self.send_json(200,{'ok':True,'message':'Wachtwoord gewijzigd. Je kunt nu inloggen.'})
        if p=='/admin/users/list':
            if not self.admin(str(data.get('token',''))):return self.error(403,'Alleen beheer heeft toegang')
            with db('identity.sqlite3') as c:
                rows=c.execute("SELECT id,display,practice_id,role,active,status,email,email_verified FROM users WHERE role='veterinarian' ORDER BY id").fetchall()
            return self.send_json(200,{'users':[dict(row) for row in rows]})
        if p=='/admin/users/email-code':
            if not self.admin(str(data.get('token',''))):return self.error(403,'Alleen beheer heeft toegang')
            name=str(data.get('username',''))[:64];now=int(time.time())
            with db('identity.sqlite3') as c:
                row=c.execute("SELECT email FROM users WHERE id=? AND role='veterinarian' AND email<>''",(name,)).fetchone()
                if not row or not email_valid(row['email']):return self.error(400,'Dierenarts heeft geen geldig e-mailadres')
                previous=c.execute('SELECT created FROM email_challenges WHERE user_id=?',(name,)).fetchone()
                if previous and previous['created']>now-60:return self.error(429,'Wacht even voordat je een nieuwe code aanvraagt')
                challenge_id=secrets.token_urlsafe(32);code=f'{secrets.randbelow(1000000):06d}'
                try:code_hash=email_code_digest(challenge_id,name,code)
                except RuntimeError:return self.error(503,'E-mailverificatie is tijdelijk niet beschikbaar')
                c.execute('DELETE FROM email_challenges WHERE user_id=?',(name,))
                c.execute('INSERT INTO email_challenges VALUES(?,?,?,?,?,0)',(challenge_id,name,code_hash,now+900,now))
            try:send_mfa_email(row['email'],code,'email_verification')
            except Exception:
                with db('identity.sqlite3') as c:c.execute('DELETE FROM email_challenges WHERE id=?',(challenge_id,))
                return self.error(503,'E-mail kon niet veilig worden verzonden')
            return self.send_json(200,{'ok':True,'message':'Verificatiecode verzonden naar het geregistreerde e-mailadres.'})
        if p=='/admin/users/status':
            if not self.admin(str(data.get('token',''))):return self.error(403,'Alleen beheer heeft toegang')
            name=str(data.get('username',''))[:64];approved=data.get('approved') is True
            with db('identity.sqlite3') as c:
                user_row=c.execute("SELECT email,email_verified FROM users WHERE id=? AND role='veterinarian'",(name,)).fetchone()
                if not user_row:return self.error(404,'Dierenarts niet gevonden')
                if approved and (not user_row['email_verified'] or not email_valid(user_row['email'])):return self.error(400,'Bevestig eerst het e-mailadres voordat je het account goedkeurt')
                cursor=c.execute("UPDATE users SET active=?,status=? WHERE id=? AND role='veterinarian'",(int(approved),'approved' if approved else 'disabled',name))
                if not cursor.rowcount:return self.error(404,'Dierenarts niet gevonden')
                if not approved:
                    c.execute('DELETE FROM sessions WHERE user_id=?',(name,))
                    c.execute('DELETE FROM login_challenges WHERE user_id=?',(name,))
            return self.send_json(200,{'ok':True})
        if p=='/admin/users/update':
            if not self.admin(str(data.get('token',''))):return self.error(403,'Alleen beheer heeft toegang')
            name=str(data.get('username',''))[:64];display=str(data.get('display','')).strip();practice=str(data.get('practice_id','')).strip();email=str(data.get('email','')).strip()
            if not display or len(display)>100 or not practice or len(practice)>100 or not email_valid(email):return self.error(400,'Naam, praktijk en geldig e-mailadres zijn verplicht')
            with db('identity.sqlite3') as c:
                old=c.execute("SELECT email FROM users WHERE id=? AND role='veterinarian'",(name,)).fetchone()
                if not old:return self.error(404,'Dierenarts niet gevonden')
                cursor=c.execute("UPDATE users SET display=?,practice_id=?,email=?,email_verified=CASE WHEN email=? THEN email_verified ELSE 0 END WHERE id=? AND role='veterinarian'",
                                 (display,practice,email,old['email'],name))
                if not cursor.rowcount:return self.error(404,'Dierenarts niet gevonden')
                if email!=old['email']:
                    c.execute('DELETE FROM email_challenges WHERE user_id=?',(name,))
                    c.execute('DELETE FROM login_challenges WHERE user_id=?',(name,))
                    c.execute('DELETE FROM sessions WHERE user_id=?',(name,))
            return self.send_json(200,{'ok':True})
        if p=='/admin/users/reset-code':
            if not self.admin(str(data.get('token',''))):return self.error(403,'Alleen beheer heeft toegang')
            name=str(data.get('username',''))[:64];code=secrets.token_urlsafe(24)
            with db('identity.sqlite3') as c:
                row=c.execute("SELECT id FROM users WHERE id=? AND role='veterinarian' AND active=1 AND status='approved'",(name,)).fetchone()
                if not row:return self.error(404,'Actieve dierenarts niet gevonden')
                c.execute('DELETE FROM password_resets WHERE user_id=?',(name,))
                c.execute('INSERT INTO password_resets VALUES(?,?,?)',(digest(code),name,int(time.time())+900))
            return self.send_json(200,{'code':code,'expires_in':900})
        if p=='/login':
            name=str(data.get('username',''))[:100];pwd=str(data.get('password',''))[:200]
            with db('identity.sqlite3') as c:
                row=c.execute('SELECT * FROM users WHERE id=?',(name,)).fetchone()
                # Perform hash even when username missing to reduce trivial timing differences.
                valid=pw_verify(pwd,row['password_hash'] if row else pw_hash('unused'))
                if not row or not row['active'] or row['status']!='approved' or not valid:return self.error(401,'Ongeldige inloggegevens')
                if not row['email_verified'] or not email_valid(row['email']):return self.error(403,'Neem contact op met beheer om je e-mailadres te laten bevestigen')
                now=int(time.time())
                previous=c.execute('SELECT id,created FROM login_challenges WHERE user_id=?',(name,)).fetchone()
                if previous and previous['created']>now-60:
                    return self.send_json(200,{'mfa_required':True,'challenge_id':previous['id'],'message':'Gebruik de eerder verstuurde code. Vraag over een minuut een nieuwe aan.'})
                challenge_id=secrets.token_urlsafe(32);code=f'{secrets.randbelow(1000000):06d}'
                try:code_hash=mfa_digest(challenge_id,name,code)
                except RuntimeError:return self.error(503,'Inloggen is tijdelijk niet beschikbaar')
                c.execute('DELETE FROM login_challenges WHERE user_id=?',(name,))
                c.execute('INSERT INTO login_challenges VALUES(?,?,?,?,?,0)',(challenge_id,name,code_hash,now+600,now))
                recipient=row['email']
            try:send_mfa_email(recipient,code)
            except Exception:
                with db('identity.sqlite3') as c:c.execute('DELETE FROM login_challenges WHERE id=?',(challenge_id,))
                return self.error(503,'Inloggen is tijdelijk niet beschikbaar omdat e-mail niet veilig kan worden verzonden')
            return self.send_json(200,{'mfa_required':True,'challenge_id':challenge_id,'message':'Er is een inlogcode naar je geregistreerde e-mailadres gestuurd.'})
        if p=='/logout':
            with db('identity.sqlite3') as c:c.execute('DELETE FROM sessions WHERE token_hash=?',(digest(self.header_token()),))
            return self.send_json(200,{'ok':True})
        if p=='/introspect':
            if not self.internal(): return self.error(403,'Interne service vereist')
            return self.send_json(200,{'user':session(str(data.get('token','')))})
        if p=='/authorize':
            if not self.internal():return self.error(403,'Interne service vereist')
            user=session(str(data.get('token','')))
            if not user:return self.error(401,'Sessie verlopen')
            action=str(data.get('action',''));chip=str(data.get('chip',''));ref=str(data.get('consultation',''))
            reason=str(data.get('purpose',''))
            permitted=False
            if action=='read_signals' and user['role']=='veterinarian' and reason in ('clinical_care','welfare_assessment') and len(chip)==15 and chip.isdigit():
                with db('identity.sqlite3') as c:
                    row=c.execute('SELECT 1 FROM consultations WHERE id=? AND user_id=? AND chip=? AND status=?',(ref,user['id'],chip,'approved')).fetchone()
                    permitted=bool(row)
            if action=='create_signal' and user['role']=='veterinarian' and reason=='welfare_assessment' and len(chip)==15 and chip.isdigit():
                with db('identity.sqlite3') as c: permitted=bool(c.execute('SELECT 1 FROM consultations WHERE id=? AND user_id=? AND chip=? AND status=?',(ref,user['id'],chip,'approved')).fetchone())
            if action=='admin_manage' and user['role']=='admin':permitted=True
            return self.send_json(200,{'allow':permitted,'subject':user['id'],'practice_id':user['practice_id'],'role':user['role'],'policy':'RBAC + consultation-bound ABAC v0.2'})
        return self.error(404,'Niet gevonden')
    def do_GET(self):
        if self.route()=='/me':
            user=session(self.header_token())
            return self.send_json(200,{'user':user}) if user else self.error(401,'Niet ingelogd')
        return self.error(404,'Niet gevonden')
    def admin(self,token):
        user=session(token)
        return bool(user and user['role']=='admin')
def main():
    init();ThreadingHTTPServer(('127.0.0.1',PORT),Api).serve_forever()
if __name__=='__main__':main()
