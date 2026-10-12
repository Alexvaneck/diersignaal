import os, time, secrets, hashlib, hmac
from http.server import ThreadingHTTPServer
from .common import Handler,db,pw_hash,pw_verify
PORT=int(os.environ.get('IDENTITY_PORT','8101'))
def init():
    with db('identity.sqlite3') as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, display TEXT NOT NULL, practice_id TEXT NOT NULL, role TEXT NOT NULL, password_hash TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id),expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS consultations(id TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id), chip TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('approved','pending','revoked')));''')
        if not c.execute('SELECT 1 FROM users').fetchone():
            demo_pw=os.environ.get('DIERSIGNAAL_DEMO_PASSWORD','PilotDemo!2026')
            c.executemany('INSERT INTO users VALUES(?,?,?,?,?,1)',[
                ('arts.west','Dr. Noor de Vries','west','veterinarian',pw_hash(demo_pw)),
                ('arts.noord','Dr. Sam Bakker','noord','veterinarian',pw_hash(demo_pw)),
                ('reviewer','Juridisch beoordelaar','review','auditor',pw_hash(demo_pw))])
            c.executemany('INSERT INTO consultations VALUES(?,?,?,?)',[
                ('CONS-W-1001','arts.west','999000000000001','approved'),
                ('CONS-W-1002','arts.west','999000000000002','approved'),
                ('CONS-N-3001','arts.noord','999000000000001','approved'),
                ('CONS-W-9999','arts.west','999000000000003','revoked')])
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
            return self.send_json(200,{'allow':permitted,'subject':user['id'],'practice_id':user['practice_id'],'role':user['role'],'policy':'RBAC + consultation-bound ABAC v0.2'})
        return self.error(404,'Niet gevonden')
    def do_GET(self):
        if self.route()=='/me':
            user=session(self.header_token())
            return self.send_json(200,{'user':user}) if user else self.error(401,'Niet ingelogd')
        return self.error(404,'Niet gevonden')
def main():
    init();ThreadingHTTPServer(('127.0.0.1',PORT),Api).serve_forever()
if __name__=='__main__':main()
