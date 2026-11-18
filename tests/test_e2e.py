import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import pytest
from indiceval.core import load_tasks
from indiceval.runner import run,validate_bundle

def test_api_to_report_twice(tmp_path):
    tasks=[t for t in load_tasks() if t["type"]=="math"][:2]
    dataset=tmp_path/"tasks.jsonl";dataset.write_text("".join(json.dumps(t,ensure_ascii=False)+"\n" for t in tasks))
    answers={t["prompt"]:t["answer"] for t in tasks}
    class API(BaseHTTPRequestHandler):
        def do_POST(self):
            assert self.path=="/v1/chat/completions"
            body=json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert "answer" not in body and "tests" not in body
            result={"choices":[{"message":{"content":answers[body["messages"][-1]["content"]]}}],"usage":{"prompt_tokens":10,"completion_tokens":2}}
            self.send_response(200);self.end_headers();self.wfile.write(json.dumps(result).encode())
        def log_message(self,*a): pass
    server=ThreadingHTTPServer(("127.0.0.1",0),API)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        output=tmp_path/"run"
        report=run(model="protocol-fixture",base_url=f"http://127.0.0.1:{server.server_port}/v1",output=output,data=dataset,kind="fixture",samples=2,ks=(1,2),input_price=1,output_price=2)
        assert report["accuracy"]==1
        assert report["score_variance"]==0
        assert report["requests"]==8
        assert report["cost_usd"]==pytest.approx(.000112)
        assert validate_bundle(output,data=dataset)==report
        with pytest.raises(ValueError,match="fixtures"):validate_bundle(output,data=dataset,submission=True)
        saved=json.loads((output/"report.json").read_text());saved["accuracy"]=0
        (output/"report.json").write_text(json.dumps(saved))
        with pytest.raises(ValueError,match="raw samples"):validate_bundle(output,data=dataset)
    finally: server.shutdown();server.server_close()

def test_request_failures_count(tmp_path):
    task=next(t for t in load_tasks() if t["type"]=="math")
    p=tmp_path/"tasks.jsonl";p.write_text(json.dumps(task))
    class API(BaseHTTPRequestHandler):
        def do_POST(self):
            self.send_response(429);self.end_headers();self.wfile.write(b"private provider detail")
        def log_message(self,*a):pass
    s=ThreadingHTTPServer(("127.0.0.1",0),API)
    threading.Thread(target=s.serve_forever,daemon=True).start()
    try:
        r=run(model="failure-fixture",base_url=f"http://127.0.0.1:{s.server_port}/v1",output=tmp_path/"out",data=p,kind="fixture")
        assert r["accuracy"]==0 and r["errors"]==2
        assert "private provider detail" not in (tmp_path/"out/samples.jsonl").read_text()
    finally:s.shutdown();s.server_close()
