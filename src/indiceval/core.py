"""Dataset integrity, deterministic grading, and auditable metrics."""
import hashlib
import json
import math
import re
import statistics
import subprocess
import tempfile
import unicodedata
import uuid
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / "data/tasks.jsonl"
SANDBOX_IMAGE = "python:3.12-slim"

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def load_tasks(path=DEFAULT_DATA):
    tasks = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    ids = set()
    for t in tasks:
        required = {"id","type","language","prompt","answer","source_id","source_url","source_revision","license","review_status","sha256"}
        if not required <= t.keys():
            raise ValueError("Task missing required fields")
        if t["id"] in ids:
            raise ValueError("Duplicate task id")
        ids.add(t["id"])
        if t["type"] not in {"code","math","causal","reading"}:
            raise ValueError("Unknown task type")
        if t["sha256"] != digest({k:v for k,v in t.items() if k != "sha256"}):
            raise ValueError(f"Task hash mismatch: {t['id']}")
        if not t["prompt"] or not t["answer"]:
            raise ValueError("Empty task prompt/answer")
    if not tasks:
        raise ValueError("Empty dataset")
    return tasks

def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).strip().split())

def numeric(text):
    text = normalize(text)
    text = "".join(str(unicodedata.digit(c)) if c.isdigit() else c for c in text)
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", text):
        raise ValueError("Expected a single finite number")
    result = Decimal(text)
    if not result.is_finite():
        raise ValueError("Non-finite number")
    return result

def unfence(text):
    text = text.strip()
    fence=chr(96)*3
    match = re.fullmatch(fence+r"(?:python)?\s*\n(.*?)\n"+fence, text, re.S)
    return match.group(1) if match else text

def sandbox(code, tests, entry_point, timeout=8, image=SANDBOX_IMAGE):
    """No network, no host mounts, read-only root, unprivileged bounded process."""
    name = "indiceval-" + uuid.uuid4().hex
    marker = uuid.uuid4().hex
    payload = code + "\n\n" + tests + f"\ncheck({entry_point})\nprint({marker!r})\n"
    command = ["docker","run","--rm","--name",name,"--network=none","--read-only",
               "--cap-drop=ALL","--security-opt=no-new-privileges","--pids-limit=32",
               "--memory=256m","--ulimit=fsize=1048576:1048576","--cpus=1","--user=65534:65534",
               "--tmpfs=/tmp:rw,noexec,nosuid,size=16m","-i",image,"python","-I","-"]
    try:
        with tempfile.TemporaryFile() as out:
            result = subprocess.run(command,input=payload.encode(),stdout=out,stderr=out,timeout=timeout)
            out.seek(0); diagnostic=out.read(1_048_577).decode(errors="replace")
        if result.returncode in (125,126,127):
            raise RuntimeError("Docker sandbox unavailable: "+diagnostic[:200])
        passed = result.returncode == 0 and marker in diagnostic.splitlines()
        return passed, None if passed else "code_test_failed"
    except subprocess.TimeoutExpired:
        subprocess.run(["docker","rm","-f",name],capture_output=True,timeout=10)
        return False, "code_timeout"
    except FileNotFoundError as exc:
        raise RuntimeError("Docker is required for code grading") from exc

def grade(task, output, image=SANDBOX_IMAGE):
    if not isinstance(output,str) or len(output)>100_000:
        return False,"invalid_output"
    if task["type"] == "code":
        return sandbox(unfence(output),task["tests"],task["entry_point"],image=image)
    try:
        if task["type"] == "math":
            return numeric(output) == numeric(task["answer"]),None
        accepted=task.get("accepted_answers",[task["answer"]])
        return normalize(output) in {normalize(a) for a in accepted},None
    except (ValueError,InvalidOperation):
        return False,"invalid_answer_format"

def pass_at_k(n,c,k):
    if not all(isinstance(v,int) for v in (n,c,k)) or not 0 <= c <= n or not 1 <= k <= n:
        raise ValueError("Require 0 <= correct <= samples and 1 <= k <= samples")
    return 1.0 if n-c < k else 1-math.comb(n-c,k)/math.comb(n,k)

def summarize(tasks, samples, repeats, n, ks=(1,)):
    expected={(t["id"],r,s) for t in tasks for r in range(repeats) for s in range(n)}
    actual=[(s["task_id"],s["repeat"],s["sample"]) for s in samples]
    if len(actual)!=len(set(actual)) or set(actual)!=expected:
        raise ValueError("Missing, duplicated, or unexpected samples")
    if repeats<1 or n<1:
        raise ValueError("Positive repeats and samples required")
    grouped=defaultdict(list)
    for s in samples:
        if type(s["passed"]) is not bool or not math.isfinite(s["latency_s"]) or s["latency_s"]<0:
            raise ValueError("Invalid sample metric")
        if s["cost_usd"] is not None and (not math.isfinite(s["cost_usd"]) or s["cost_usd"]<0):
            raise ValueError("Invalid cost")
        grouped[(s["task_id"],s["repeat"])].append(s)
    repeat_scores=[statistics.mean(s["passed"] for s in samples if s["repeat"]==r and s["sample"]==0) for r in range(repeats)]
    latencies=sorted(s["latency_s"] for s in samples)
    costs=[s["cost_usd"] for s in samples]
    report={
      "tasks":len(tasks),"requests":len(samples),"repeats":repeats,"samples_per_task":n,
      "accuracy":statistics.mean(repeat_scores),"repeat_accuracy":repeat_scores,
      "score_variance":statistics.variance(repeat_scores) if repeats>1 else None,
      "score_range":max(repeat_scores)-min(repeat_scores),
      "pass_at_k":{str(k):statistics.mean(pass_at_k(n,sum(x["passed"] for x in group),k) for group in grouped.values()) for k in ks},
      "latency_mean_s":statistics.mean(latencies),"latency_p50_s":statistics.median(latencies),
      "latency_p95_s":latencies[math.ceil(.95*len(latencies))-1],
      "cost_usd":sum(costs) if all(c is not None for c in costs) else None,
      "cost_per_task_usd":sum(costs)/(len(tasks)*repeats) if all(c is not None for c in costs) else None,
      "cost_coverage":sum(c is not None for c in costs)/len(costs),
      "errors":sum(bool(s.get("error")) for s in samples),
    }
    report["by_type"]={}
    report["by_language"]={}
    for field,key in [("type","by_type"),("language","by_language")]:
        for value in sorted({t[field] for t in tasks}):
            ids={t["id"] for t in tasks if t[field]==value}
            report[key][value]={"tasks":len(ids),"accuracy":statistics.mean(s["passed"] for s in samples if s["task_id"] in ids and s["sample"]==0)}
    return report
