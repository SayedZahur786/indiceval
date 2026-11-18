"""End-to-end protocol diagnostic, NOT a model evaluation."""
import json,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from indiceval.core import load_tasks
from indiceval.runner import run,validate_bundle
ROOT=Path(__file__).resolve().parents[1]
answers={t['prompt']:t['answer'] for t in load_tasks()}
class ReferenceAPI(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path!='/v1/chat/completions':self.send_error(404);return
        payload=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        prompt=payload['messages'][-1]['content']
        response={'choices':[{'message':{'role':'assistant','content':answers[prompt]}}]}
        raw=json.dumps(response,ensure_ascii=False).encode()
        self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(raw)
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),ReferenceAPI)
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
    directory=ROOT/'docs/evidence/reference-run'
    report=run(model='reference-answer-fixture (not a model)',base_url=f'http://127.0.0.1:{server.server_port}/v1',output=directory,kind='fixture',repeats=2)
    validate_bundle(directory)
    print(json.dumps(report,indent=2))
finally:server.shutdown();server.server_close()
