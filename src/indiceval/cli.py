import argparse
import json
from .core import DEFAULT_DATA, load_tasks
from .runner import run, validate_bundle

def main():
    parser=argparse.ArgumentParser(description="IndicEval: reproducible Indic capability evaluation")
    subs=parser.add_subparsers(dest="command",required=True)
    validate=subs.add_parser("validate-data");validate.add_argument("--data",default=str(DEFAULT_DATA))
    evaluate=subs.add_parser("run")
    for name in ("model","base-url","output"): evaluate.add_argument("--"+name,required=True)
    evaluate.add_argument("--data",default=str(DEFAULT_DATA))
    for name,default in [("repeats",2),("samples",1),("seed",42),("max-tokens",2048)]:
        evaluate.add_argument("--"+name,type=int,default=default)
    evaluate.add_argument("--k",type=int,nargs="+",default=[1])
    evaluate.add_argument("--temperature",type=float,default=0)
    evaluate.add_argument("--timeout",type=float,default=60)
    evaluate.add_argument("--input-price",type=float)
    evaluate.add_argument("--output-price",type=float)
    evaluate.add_argument("--key-env",default="INDICEVAL_API_KEY")
    evaluate.add_argument("--limit",type=int)
    bundle=subs.add_parser("validate-run");bundle.add_argument("directory");bundle.add_argument("--submission",action="store_true");bundle.add_argument("--regrade",action="store_true");bundle.add_argument("--data",default=str(DEFAULT_DATA))
    args=vars(parser.parse_args());command=args.pop("command")
    try:
        if command=="validate-data": result={"valid_tasks":len(load_tasks(args["data"]))}
        elif command=="validate-run": result=validate_bundle(**args)
        else:
            args["ks"]=args.pop("k")
            result=run(**args)
        print(json.dumps(result,indent=2))
    except (ValueError,RuntimeError,OSError,KeyError) as exc:
        parser.exit(1,f"Error: {exc}\n")
if __name__=="__main__": main()
