import json
import pytest
from indiceval.core import grade, load_tasks, numeric, pass_at_k, summarize
from indiceval.runner import validate_url

@pytest.mark.parametrize("n,c,k,expected",[(10,0,1,0),(10,10,5,1),(10,2,1,.2),(10,2,2,17/45),(2,1,2,1)])
def test_pass_k(n,c,k,expected):
    assert pass_at_k(n,c,k)==pytest.approx(expected)

@pytest.mark.parametrize("args",[(0,0,1),(1,2,1),(3,1,4),(3,-1,1),(3,1,0)])
def test_invalid_k(args):
    with pytest.raises(ValueError): pass_at_k(*args)

def test_dataset_integrity(tmp_path):
    tasks=load_tasks()
    assert len(tasks)==200
    assert {k:sum(t["type"]==k for t in tasks) for k in ["code","math","causal","reading"]}==dict.fromkeys(["code","math","causal","reading"],50)
    tasks[0]["answer"]="tampered"
    f=tmp_path/"bad.jsonl";f.write_text(json.dumps(tasks[0]))
    with pytest.raises(ValueError,match="hash"):load_tasks(f)

def test_numeric_and_exact_grading():
    assert numeric("१८.०")==18
    assert grade({"type":"math","answer":"18"},"১৮")[0]
    assert not grade({"type":"math","answer":"18"},"18 dollars")[0]
    assert not grade({"type":"math","answer":"18"},"NaN")[0]
    assert grade({"type":"reading","answer":"কথা"},"  কথা \n")[0]
    assert not grade({"type":"causal","answer":"1"},"11")[0]

def test_missing_and_duplicate_samples():
    tasks=[{"id":"a","type":"math","language":"hi"}]
    s={"task_id":"a","repeat":0,"sample":0,"passed":True,"latency_s":.1,"cost_usd":None}
    report=summarize(tasks,[s],1,1)
    assert report["cost_usd"] is None
    assert report["score_variance"] is None
    with pytest.raises(ValueError): summarize(tasks,[s,s],1,1)
    with pytest.raises(ValueError): summarize(tasks,[s],2,1)

def test_variance_and_cost():
    tasks=[{"id":"a","type":"math","language":"hi"}]
    samples=[{"task_id":"a","repeat":r,"sample":0,"passed":r==0,"latency_s":r+1,"cost_usd":.01} for r in range(2)]
    report=summarize(tasks,samples,2,1)
    assert report["accuracy"]==.5
    assert report["score_variance"]==.5
    assert report["cost_per_task_usd"]==.01

@pytest.mark.parametrize("url",["http://example.org/v1","https://key:secret@example.org/v1","https://example.org/v1?key=x"])
def test_reject_credential_urls(url):
    with pytest.raises(ValueError): validate_url(url)
