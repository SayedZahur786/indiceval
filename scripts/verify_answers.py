"""Verify executable references, source labels, spans, and arithmetic annotations."""
import ast,json,operator,re
from pathlib import Path
from indiceval.core import load_tasks,grade,numeric
ROOT=Path(__file__).resolve().parents[1]
OPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv}
def arithmetic(s):
    node=ast.parse(s,mode="eval").body
    def visit(n):
        if isinstance(n,ast.Constant) and type(n.value) in (int,float):return n.value
        if isinstance(n,ast.BinOp) and type(n.op) in OPS:return OPS[type(n.op)](visit(n.left),visit(n.right))
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return -visit(n.operand)
        raise ValueError("Unsupported annotation")
    return visit(node)
def main():
    tasks=load_tasks();evidence=[]
    qa={x["id"]:x for x in json.loads((ROOT/"data/upstream/qa_bn.json").read_text())["examples"]}
    causal={str(x["idx"]):x for x in map(json.loads,(ROOT/"data/upstream/causal_ta.jsonl").read_text().splitlines())}
    for t in tasks:
        ok,error=grade(t,t["answer"])
        checks=["reference passes grader"]
        if t["type"]=="math":
            equations=re.findall(r"<<([^<>]+)=([^<>]+)>>",t["rationale"])
            for expression,result in equations:
                assert abs(arithmetic(expression.replace(",",""))-float(numeric(result.replace(",",""))))<1e-6,(t["id"],expression,result)
            checks.append(f"{len(equations)} upstream arithmetic annotations evaluated")
        if t["type"]=="reading":
            assert all(a in qa[t["source_item"]]["context"] for a in t["accepted_answers"]),t["id"]
            checks.append("accepted answers occur in source context")
        if t["type"]=="causal":
            assert t["answer"]==str(causal[t["source_item"]]["label"]+1)
            checks.append("label matches upstream human annotation; not an independent semantic proof")
        evidence.append({"task_id":t["id"],"task_sha256":t["sha256"],"passed":ok,"checks":checks,"error":error})
        print(t["id"],ok,flush=True)
    (ROOT/"docs/evidence/answer-verification.json").write_text(json.dumps(evidence,indent=2)+"\n")
    assert all(e["passed"] for e in evidence)
if __name__=="__main__":main()
