import unittest,tempfile,subprocess,sys,os,time,json,urllib.request,urllib.error,socket
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def freeport():
    with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
class TestPilot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        ports=set()
        while len(ports)<3: ports.add(freeport())
        cls.gateway,cls.identity,cls.signals=sorted(ports)
        cls.env=os.environ.copy();cls.env.update(DIERSIGNAAL_DATA=cls.temp.name,DIERSIGNAAL_INTERNAL_SECRET='integration-test-only-secret',GATEWAY_PORT=str(cls.gateway),IDENTITY_PORT=str(cls.identity),SIGNALS_PORT=str(cls.signals))
        cls.procs=[]
        for mod in ['identity','signals','gateway']:
            cls.procs.append(subprocess.Popen([sys.executable,'-m','services.'+mod],env=cls.env,cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE))
        for _ in range(120):
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{cls.gateway}/',timeout=.4):break
            except Exception:time.sleep(.1)
        else:raise RuntimeError('Gateway start niet: '+str([(p.poll(),p.stderr.read().decode() if p.poll() is not None else 'running') for p in cls.procs]))
        for _ in range(120):
            ready=True
            for port in (cls.identity,cls.signals):
                with socket.socket() as service:
                    if service.connect_ex(('127.0.0.1',port))!=0:
                        ready=False
                        break
            if ready:break
            time.sleep(.1)
        else:raise RuntimeError('Identity- of signalservice start niet: '+str([(p.poll(),p.stderr.read().decode() if p.poll() is not None else 'running') for p in cls.procs]))
    @classmethod
    def tearDownClass(cls):
        for p in cls.procs:p.terminate()
        for p in cls.procs:
            try:p.wait(timeout=2)
            except subprocess.TimeoutExpired:p.kill()
        cls.temp.cleanup()
    def call(self,path,payload=None,token=None):
        data=json.dumps(payload).encode() if payload is not None else None
        headers={'Content-Type':'application/json'}
        if token:headers['Authorization']='Bearer '+token
        req=urllib.request.Request(f'http://127.0.0.1:{self.gateway}/api/{path}',data=data,headers=headers)
        try:
            with urllib.request.urlopen(req,timeout=4) as r:return r.status,json.load(r)
        except urllib.error.HTTPError as e:return e.code,json.load(e)
    def login(self,name='arts.west'):
        status,result=self.call('login',{'username':name,'password':'PilotDemo!2026'})
        self.assertEqual(status,200)
        return result['token']
    def access(self,chip='999000000000001',consultation='CONS-W-1001',purpose='clinical_care'):
        return dict(chip=chip,consultation=consultation,purpose=purpose)
    def test_00_public_pages_are_available_without_login(self):
        for path,expected in [('/','DierSignaal'),('/about','Ilona van Eck'),('/about.html','Alex van Eck')]:
            with urllib.request.urlopen(f'http://127.0.0.1:{self.gateway}{path}',timeout=4) as response:
                page=response.read().decode()
                self.assertEqual(response.status,200)
                self.assertIn(expected,page)
                self.assertEqual(response.headers.get('X-Frame-Options'),'DENY')
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(f'http://127.0.0.1:{self.gateway}/services/identity.py',timeout=4)
        self.assertEqual(error.exception.code,404)
    def test_01_invalid_password(self):
        self.assertEqual(self.call('login',{'username':'arts.west','password':'wrong'})[0],401)
    def test_02_anonymous_denied(self):
        self.assertEqual(self.call('lookup',self.access())[0],403)
    def test_03_correct_consult_allowed(self):
        status,data=self.call('lookup',self.access(),self.login())
        self.assertEqual(status,200)
        self.assertEqual(data['animal']['name'],'Bowie')
        self.assertEqual(len(data['signals']),2)
    def test_04_wrong_consult_denied(self):
        self.assertEqual(self.call('lookup',self.access(consultation='CONS-N-3001'),self.login())[0],403)
    def test_05_other_chip_denied(self):
        self.assertEqual(self.call('lookup',self.access(chip='999000000000003'),self.login())[0],403)
    def test_06_wrong_purpose_denied(self):
        self.assertEqual(self.call('lookup',self.access(purpose='curiosity'),self.login())[0],403)
    def test_07_auditor_denied(self):
        self.assertEqual(self.call('lookup',self.access(),self.login('reviewer'))[0],403)
    def test_08_logout_revokes_session(self):
        token=self.login();self.assertEqual(self.call('logout',{},token)[0],200)
        self.assertEqual(self.call('lookup',self.access(),token)[0],403)
    def test_09_create_draft_not_published(self):
        token=self.login()
        request={**self.access(purpose='welfare_assessment'), 'observed':'Objectieve demo-observatie','method':'Onderzoek','caretaker_statement':'Onbekend','interpretation':'Geen conclusie','followup':'Collegiaal overleg'}
        st,d=self.call('signals',request,token);self.assertEqual(st,201);self.assertEqual(d['status'],'draft')
        st,result=self.call('lookup',self.access(),token)
        self.assertEqual(len(result['signals']),2)
    def test_10_create_wrong_purpose_denied(self):
        token=self.login();self.assertEqual(self.call('signals',self.access(purpose='clinical_care'),token)[0],403)
    def test_11_identity_service_not_accessible_through_gateway(self):
        self.assertEqual(self.call('introspect',{},self.login())[0],404)
    def test_12_registration_requires_admin_approval(self):
        payload={'username':'new.vet','display':'Dr. Demo','practice_id':'demo-practice','password':'SecureDemoPass!2026','role':'admin'}
        status,result=self.call('register',payload)
        self.assertEqual(status,201)
        self.assertEqual(result['status'],'pending')
        self.assertEqual(self.call('login',{'username':'new.vet','password':payload['password']})[0],401)
        admin=self.login('beheerder')
        status,data=self.call('admin/users/list',{},admin)
        self.assertEqual(status,200)
        new_user=next(user for user in data['users'] if user['id']=='new.vet')
        self.assertEqual(new_user['role'],'veterinarian')
        self.assertEqual(self.call('admin/users/status',{'username':'new.vet','approved':True},self.login())[0],403)
        profile={'username':'new.vet','display':'Dr. Updated Demo','practice_id':'updated-practice'}
        self.assertEqual(self.call('admin/users/update',profile,self.login())[0],403)
        self.assertEqual(self.call('admin/users/status',{'username':'new.vet','approved':True},admin)[0],200)
        self.assertEqual(self.call('admin/users/update',profile,admin)[0],200)
        status,data=self.call('admin/users/list',{},admin)
        updated=next(user for user in data['users'] if user['id']=='new.vet')
        self.assertEqual((updated['display'],updated['practice_id']),('Dr. Updated Demo','updated-practice'))
        self.assertEqual(self.call('login',{'username':'new.vet','password':payload['password']})[0],200)
    def test_13_admin_can_issue_one_time_password_recovery(self):
        admin=self.login('beheerder')
        status,result=self.call('admin/users/reset-code',{'username':'arts.west'},admin)
        self.assertEqual(status,200)
        code=result['code']
        payload={'username':'arts.west','code':code,'password':'ChangedDemoPass!2026'}
        self.assertEqual(self.call('password-reset',payload)[0],200)
        self.assertEqual(self.call('login',{'username':'arts.west','password':'PilotDemo!2026'})[0],401)
        self.assertEqual(self.call('login',{'username':'arts.west','password':payload['password']})[0],200)
        self.assertEqual(self.call('password-reset',payload)[0],400)
    def test_14_admin_manages_dog_and_cat_records(self):
        admin=self.login('beheerder')
        animal={'chip':'999000000000099','name':'Luna','species':'Kat','breed':'Europese korthaar'}
        status,_=self.call('admin/animals/create',animal,admin)
        self.assertEqual(status,201)
        status,data=self.call('admin/animals/list',{},admin)
        self.assertEqual(status,200)
        created=next(item for item in data['animals'] if item['chip']==animal['chip'])
        self.assertEqual((created['species'],created['breed']),('Kat','Europese korthaar'))
        changed={**animal,'name':'Luna II','species':'Hond','breed':'Demo-ras'}
        self.assertEqual(self.call('admin/animals/update',changed,admin)[0],200)
        self.assertEqual(self.call('admin/animals/list',{},self.login('arts.noord'))[0],403)
        status,data=self.call('admin/animals/list',{},admin)
        updated=next(item for item in data['animals'] if item['chip']==animal['chip'])
        self.assertEqual((updated['name'],updated['species']),('Luna II','Hond'))
        self.assertEqual(self.call('admin/animals/create',{**animal,'species':'Konijn'},admin)[0],400)
if __name__=='__main__':unittest.main()
