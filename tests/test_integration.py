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
        for _ in range(60):
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{cls.gateway}/',timeout=.4):break
            except Exception:time.sleep(.1)
        else:raise RuntimeError('Gateway start niet: '+str([(p.poll(),p.stderr.read().decode() if p.poll() is not None else 'running') for p in cls.procs]))
        time.sleep(.2)
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
if __name__=='__main__':unittest.main()
