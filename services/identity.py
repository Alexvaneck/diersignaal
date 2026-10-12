import os, time, secrets, hashlib, hmac, re, sqlite3
from http.server import ThreadingHTTPServer
from .common import Handler,db,pw_hash,pw_verify
PORT=int(os.environ.get('IDENTITY_PORT','8101'))
def init():
    with db('identity.sqlite3') as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, display TEXT NOT NULL, practice_id TEXT NOT NULL, role TEXT NOT NULL, password_hash TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1, status TEXT NOT NULL DEFAULT 'approved');
        CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id),expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS consultations(id TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id), chip TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('approved','pending','revoked')));
        CREATE TABLE IF NOT EXISTS password_resets(token_hash TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id),expires INTEGER NOT NULL);''')
        if 'status' not in {row['name'] for row in c.execute('PRAGMA table_info(users)')}:
            c.execute("ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'approved'")
        if not c.execute('SELECT 1 FROM users').fetchone():
            demo_pw=os.environ.get('DIERSIGNAAL_DEMO_PASSWORD','PilotDemo!2026')
            c.executemany("INSERT INTO users(id,display,practice_id,role,password_hash,active,status) VALUES(?,?,?,?,?,1,'approved')",[
                ('arts.west','Dr. Noor de Vries','west','veterinarian',pw_hash(demo_pw)),
                ('arts.noord','Dr. Sam Bakker','noord','veterinarian',pw_hash(demo_pw)),
                ('reviewer','Juridisch beoordelaar','review','auditor',pw_hash(demo_pw))])
            c.executemany('INSERT INTO consultations VALUES(?,?,?,?)',[
                ('CONS-W-1001','arts.west','999000000000001','approved'),
                ('CONS-W-1002','arts.west','999000000000002','approved'),
                ('CONS-N-3001','arts.noord','999000000000001','approved'),
                ('CONS-W-9999','arts.west','999000000000003','revoked')])
        admin_password=os.environ.get('DIERSIGNAAL_ADMIN_PASSWORD',os.environ.get('DIERSIGNAAL_DEMO_PASSWORD','PilotDemo!2026'))
        c.execute('INSERT OR IGNORE INTO users(id,display,practice_id,role,password_hash,active,status) VALUES(?,?,?,?,?,1,?)',
                  ('beheerder','Demo-beheerder','beheer','admin',pw_hash(admin_password),'approved'))
def digest(token): return hashlib.sha256(token.encode()).hexdigest()
def session(token):
    if not token: return None
    with db('identity.sqlite3') as c:
        row=c.execute('''SELECT u.id,u.display,u.practice_id,u.role FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires>? AND u.active=1''',(digest(token),int(time.time()))).fetchone()
        return dict(row) if row else None
class Api(Handler):
    def do_POST(self):
        p=self.route()
        try: data=self.body()
        except Exception: return self.error(400,'Ongeldige JSON')
        if p=='/register':
            name=str(data.get('username','')).strip();display=str(data.get('display','')).strip();practice=str(data.get('practice_id','')).strip();new_secret=str(data.get('password',''))
            if not re.fullmatch(r'[A-Za-z0-9._-]{3,64}',name) or not display or len(display)>100 or not practice or len(practice)>100 or len(new_secret)<12 or len(new_secret)>200:
                return self.error(400,'Controleer gebruikersnaam, praktijk, naam en wachtwoord (minimaal 12 tekens)')
            with db('identity.sqlite3') as c:
                try:c.execute("INSERT INTO users(id,display,practice_id,role,password_hash,active,status) VALUES(?,?,?,?,?,0,'pending')",(name,display,practice,'veterinarian',pw_hash(new_secret)))
                except sqlite3.IntegrityError:return self.error(409,'Deze gebruikersnaam is al in gebruik')
            return self.send_json(201,{'status':'pending','message':'Registratie ontvangen; een beheerder moet het account eerst goedkeuren.'})
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
            return self.send_json(200,{'ok':True,'message':'Wachtwoord gewijzigd. Je kunt nu inloggen.'})
        if p=='/admin/users/list':
            if not self.admin(str(data.get('token',''))):return self.error(403,'Alleen beheer heeft toegang')
            with db('identity.sqlite3') as c:
                rows=c.execute("SELECT id,display,practice_id,role,active,status FROM users WHERE role='veterinarian' ORDER BY id").fetchall()
            return self.send_json(200,{'users':[dict(row) for row in rows]})
        if p=='/admin/users/status':
            if not self.admin(str(data.get('token',''))):return self.error(403,'Alleen beheer heeft toegang')
            name=str(data.get('username',''))[:64];approved=data.get('approved') is True
            with db('identity.sqlite3') as c:
                cursor=c.execute("UPDATE users SET active=?,status=? WHERE id=? AND role='veterinarian'",(int(approved),'approved' if approved else 'disabled',name))
                if not cursor.rowcount:return self.error(404,'Dierenarts niet gevonden')
                if not approved:c.execute('DELETE FROM sessions WHERE user_id=?',(name,))
            return self.send_json(200,{'ok':True})
        if p=='/admin/users/update':
            if not self.admin(str(data.get('token',''))):return self.error(403,'Alleen beheer heeft toegang')
            name=str(data.get('username',''))[:64];display=str(data.get('display','')).strip();practice=str(data.get('practice_id','')).strip()
            if not display or len(display)>100 or not practice or len(practice)>100:return self.error(400,'Naam en praktijk zijn verplicht (maximaal 100 tekens)')
            with db('identity.sqlite3') as c:
                cursor=c.execute("UPDATE users SET display=?,practice_id=? WHERE id=? AND role='veterinarian'",(display,practice,name))
                if not cursor.rowcount:return self.error(404,'Dierenarts niet gevonden')
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
                if not row or not row['active'] or not valid:return self.error(401,'Ongeldige inloggegevens')
                token=secrets.token_urlsafe(36)
                c.execute('DELETE FROM sessions WHERE expires<?',(int(time.time()),))
                c.execute('INSERT INTO sessions VALUES(?,?,?)',(digest(token),name,int(time.time())+1800))
            return self.send_json(200,{'token':token,'user':{'id':row['id'],'display':row['display'],'role':row['role'],'practice_id':row['practice_id']},'expires_in':1800})
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
