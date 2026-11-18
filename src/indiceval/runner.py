import hashlib
import json
import math
import os
import platform
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
import httpx
from .core import DEFAULT_DATA, SANDBOX_IMAGE, grade, load_tasks, summarize

def validate_url(url):
    parsed=urlsplit(url)
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Endpoint must not contain credentials, query parameters, or fragments")
    if parsed.scheme!="https" and not (parsed.scheme=="http" and parsed.hostname in {"localhost","127.0.0.1","::1"}):
        raise ValueError("HTTPS required except for local endpoints")
    return url.rstrip("/")

def run(*, model, base_url, output, data=DEFAULT_DATA, repeats=2, samples=1, ks=(1,),
        temperature=0.0, seed=42, timeout=60, max_tokens=2048, input_price=None,
        output_price=None, key_env="INDICEVAL_API_KEY", kind="model", limit=None):
    base_url=validate_url(base_url)
    if not model.strip() or repeats<1 or samples<1 or (not math.isfinite(timeout) or timeout<=0) or max_tokens<1:
        raise ValueError("Invalid run configuration")
    if not math.isfinite(temperature) or not 0<=temperature<=2:
        raise ValueError("Temperature must be finite and between 0 and 2")
    if any(k<1 or k>samples for k in ks):
        raise ValueError("Each k must be between 1 and samples")
    for p in (input_price,output_price):
        if p is not None and (not math.isfinite(p) or p<0): raise ValueError("Invalid price")
    if limit is not None and limit<1: raise ValueError("Limit must be positive")
    tasks=load_tasks(data)
    if limit: tasks=tasks[:limit]
    target=Path(output)
    if target.exists(): raise ValueError("Output already exists; choose a new run directory")
    image=SANDBOX_IMAGE
    if any(t["type"]=="code" for t in tasks):
        try:
            image=subprocess.check_output(["docker","image","inspect",SANDBOX_IMAGE,"--format","{{.Id}}"],text=True,stderr=subprocess.DEVNULL).strip()
        except (subprocess.CalledProcessError,FileNotFoundError) as exc:
            raise RuntimeError("Run docker pull python:3.12-slim before evaluating code") from exc
    target.mkdir(parents=True)
    try: commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError: commit=None
    metadata={"schema_version":1,"id":uuid.uuid4().hex,"kind":kind,"model":model,
        "endpoint":base_url,"created_at":datetime.now(timezone.utc).isoformat(),
        "dataset_sha256":hashlib.sha256(Path(data).read_bytes()).hexdigest(),
        "task_ids":[t["id"] for t in tasks],"repeats":repeats,"samples":samples,"ks":list(ks),
        "temperature":temperature,"seed":seed,"max_tokens":max_tokens,"timeout_s":timeout,
        "input_price_per_million":input_price,"output_price_per_million":output_price,
        "git_commit":commit,"working_tree_dirty":bool(subprocess.check_output(["git","status","--porcelain"],text=True)),"python":platform.python_version(),"sandbox_image":image}
    (target/"run.json").write_text(json.dumps(metadata,indent=2)+"\n")
    headers={}
    if os.environ.get(key_env): headers["Authorization"]="Bearer "+os.environ[key_env]
    records=[]
    with httpx.Client(timeout=timeout,headers=headers,follow_redirects=False) as client, (target/"samples.jsonl").open("w") as out:
        for repeat in range(repeats):
            for task in tasks:
                for index in range(samples):
                    start=time.perf_counter(); error=None; usage=None; content=""
                    try:
                        response=client.post(base_url+"/chat/completions",json={
                            "model":model,"messages":[{"role":"system","content":"Follow the task's output format exactly. Return only the answer or complete Python code."},{"role":"user","content":task["prompt"]}],
                            "temperature":temperature,"seed":seed+repeat*samples+index,"max_tokens":max_tokens})
                        response.raise_for_status(); body=response.json()
                        content=body["choices"][0]["message"]["content"]
                        if not isinstance(content,str): raise ValueError("Non-text output")
                        usage=body.get("usage")
                        if not isinstance(usage,dict): usage=None
                    except (httpx.HTTPError,ValueError,KeyError,IndexError,TypeError) as exc:
                        error=type(exc).__name__
                    latency=time.perf_counter()-start
                    passed=False
                    if not error:
                        passed,error=grade(task,content,image=image)
                    cost=None
                    if usage and input_price is not None and output_price is not None:
                        p,c=usage.get("prompt_tokens"),usage.get("completion_tokens")
                        if type(p) is int and type(c) is int and p>=0 and c>=0:
                            cost=(p*input_price+c*output_price)/1_000_000
                    record={"task_id":task["id"],"repeat":repeat,"sample":index,"output":content,
                        "passed":passed,"error":error,"usage":usage,"latency_s":latency,"cost_usd":cost}
                    records.append(record); out.write(json.dumps(record,ensure_ascii=False)+"\n");out.flush()
            print(f"Repetition {repeat+1}/{repeats} complete",flush=True)
    report=summarize(tasks,records,repeats,samples,ks)
    (target/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

def validate_bundle(directory,data=DEFAULT_DATA,submission=False,regrade=False):
    p=Path(directory);metadata=json.loads((p/"run.json").read_text())
    tasks=load_tasks(data)
    if metadata["dataset_sha256"]!=hashlib.sha256(Path(data).read_bytes()).hexdigest():
        raise ValueError("Dataset hash mismatch")
    selected=[t for t in tasks if t["id"] in metadata["task_ids"]]
    if len(selected)!=len(metadata["task_ids"]): raise ValueError("Invalid task IDs")
    records=[json.loads(x) for x in (p/"samples.jsonl").read_text().splitlines()]
    report=summarize(selected,records,metadata["repeats"],metadata["samples"],metadata["ks"])
    if report!=json.loads((p/"report.json").read_text()):
        raise ValueError("Report does not match raw samples")
    if submission:
        if metadata["kind"]!="model": raise ValueError("Diagnostic fixtures cannot rank")
        if len(selected)!=len(tasks): raise ValueError("Full dataset required")
        if metadata["repeats"]<2: raise ValueError("At least two repetitions required")
    if regrade or submission:
        by_id={t["id"]:t for t in selected}
        for sample in records:
            if sample["error"] in {"HTTPStatusError","ConnectError","ReadTimeout","ConnectTimeout","RemoteProtocolError","ValueError","KeyError","IndexError","TypeError"}:
                if sample["passed"]: raise ValueError("Request failures cannot pass")
                continue
            passed,_=grade(by_id[sample["task_id"]],sample["output"])
            if passed!=sample["passed"]: raise ValueError("Stored grade does not match output")
        for sample in records:
            expected_cost=None
            usage=sample.get("usage")
            ip,op=metadata.get("input_price_per_million"),metadata.get("output_price_per_million")
            if isinstance(usage,dict) and ip is not None and op is not None:
                p,c=usage.get("prompt_tokens"),usage.get("completion_tokens")
                if type(p) is int and type(c) is int and p>=0 and c>=0:
                    expected_cost=(p*ip+c*op)/1_000_000
            if sample["cost_usd"]!=expected_cost: raise ValueError("Stored cost does not match usage/prices")
    return report
