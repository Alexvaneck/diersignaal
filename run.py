"""Start drie lokaal gebonden, gescheiden HTTP-services voor de fictieve pilot."""
import os,sys,subprocess,time,secrets,signal
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('DIERSIGNAAL_INTERNAL_SECRET',secrets.token_urlsafe(40))
children=[]
try:
    for module in ('identity','signals','gateway'):
        children.append(subprocess.Popen([sys.executable,'-m',f'services.{module}'],cwd=ROOT,env=os.environ.copy()))
    print('DierSignaal pilot: http://127.0.0.1:'+os.environ.get('GATEWAY_PORT','8100'),flush=True)
    print('Voorbeeld: arts.west / '+os.environ.get('DIERSIGNAAL_DEMO_PASSWORD','PilotDemo!2026'),flush=True)
    print('Demo met fictieve gegevens. Geen productiebeveiliging.',flush=True)
    while all(p.poll() is None for p in children):time.sleep(.5)
finally:
    for p in children:p.terminate()
    for p in children:
        try:p.wait(timeout=3)
        except subprocess.TimeoutExpired:p.kill()
