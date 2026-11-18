"""Pin upstream data, preserve licences, and assemble the auditable 200-task release."""
import gzip, hashlib, json, pathlib, re, subprocess, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[1]
def fetch(url):
    return urllib.request.urlopen(url, timeout=60).read()
def revision(repo, branch):
    return subprocess.check_output(['gh','api',f'repos/{repo}/commits/{branch}','--jq','.sha'], text=True).strip()
def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')
def main():
    sources = {
      'humaneval': {'repo':'openai/human-eval','branch':'master','path':'data/HumanEval.jsonl.gz','file':'humaneval.jsonl','license':'MIT','license_path':'LICENSE','review':'English problems human-written; new Hinglish adaptations are not human-reviewed.','authors':'Mark Chen et al.; OpenAI','paper':'https://arxiv.org/abs/2107.03374'},
      'xcopa': {'repo':'cambridgeltl/xcopa','branch':'master','path':'data/ta/test.ta.jsonl','file':'causal_ta.jsonl','license':'CC-BY-4.0','license_path':'LICENSE.md','review':'Upstream translated and reannotated by human annotators; individual review identities not published.','authors':'Edoardo M. Ponti et al.','paper':'https://aclanthology.org/2020.emnlp-main.185/'},
      'xquad-in': {'repo':'google-research-datasets/indic-gen-bench','branch':'main','path':'xquad_in/xquad_bn_test.json','file':'qa_bn.json','license':'CC-BY-SA-4.0','license_path':'LICENSE-CC-BY-SA4.0','review':'Upstream professional human translations; individual task reviewer identities not published.','authors':'Harman Singh, Nitish Gupta, Shikhar Bharadwaj, Dinesh Tewari, Partha Talukdar; XQuAD/SQuAD source authors','paper':'https://aclanthology.org/2024.acl-long.595/'},
    }
    upstream=ROOT/'data/upstream'; upstream.mkdir(exist_ok=True)
    licenses=ROOT/'data/licenses'; licenses.mkdir(exist_ok=True)
    if (ROOT/'data/sources.json').exists():
        sources=json.loads((ROOT/'data/sources.json').read_text())
    else:
        for key,s in sources.items():
            sha=revision(s['repo'],s['branch']); s['revision']=sha
            base=f"https://raw.githubusercontent.com/{s['repo']}/{sha}/"
            raw=fetch(base+s['path']); raw=gzip.decompress(raw) if s['path'].endswith('.gz') else raw
            (upstream/s['file']).write_bytes(raw)
            s['sha256']=hashlib.sha256(raw).hexdigest(); s['url']=f"https://github.com/{s['repo']}/blob/{sha}/{s['path']}"
            (licenses/(key+'.txt')).write_bytes(fetch(base+s['license_path']))
            (upstream/(key+'-README.md')).write_bytes(fetch(base+'README.md'))
            s['consent']='Published research dataset reused under its stated licence; no new participant collection. Individual consent records are not supplied upstream.'
        info=json.loads(fetch('https://huggingface.co/api/datasets/nvidia/GSM8K-Hi'));sha=info['sha']
        base=f'https://huggingface.co/datasets/nvidia/GSM8K-Hi/resolve/{sha}/'
        raw=fetch(base+'test.jsonl');(upstream/'math_hi.jsonl').write_bytes(raw)
        (upstream/'gsm8k-hi-README.md').write_bytes(fetch(base+'README.md'))
        sources['gsm8k-hi']={'revision':sha,'file':'math_hi.jsonl','sha256':hashlib.sha256(raw).hexdigest(),'url':base+'test.jsonl','license':'CC-BY-4.0','review':'Dataset card explicitly states human review and correction of translated samples.','authors':'NVIDIA Corporation; original GSM8K by Karl Cobbe et al.','consent':'Published fictional math problems under CC BY 4.0; no new participant collection. Individual annotator consent records not supplied.'}
        (licenses/'gsm8k-hi.txt').write_bytes((licenses/'xcopa.txt').read_bytes())
        write_json(ROOT/'data/sources.json',sources)
    rows=lambda f:[json.loads(x) for x in (upstream/f).read_text().splitlines()]
    tasks=[]
    translations=json.loads((ROOT/'data/hinglish.json').read_text())
    for i,d in enumerate(rows('humaneval.jsonl')[:50]):
        # Only change the target function's docstring; retain helper code.
        pos=d['prompt'].index('def '+d['entry_point']+'(')
        stub=d['prompt'][:pos]+re.sub(r'"""(.*?)"""','"""'+translations[i]+'"""',d['prompt'][pos:],count=1,flags=re.S)
        prompt='Python function implement karo. Poora runnable code return karo, explanation nahi.\n\n'+stub
        tasks.append(dict(id=f'code-{i:03}',type='code',language='hi-Latn',prompt=prompt,english_control=d['prompt'],answer=d['prompt']+d['canonical_solution'],tests=d['test'],entry_point=d['entry_point'],source_id='humaneval',source_item=d['task_id'],review_status='adaptation-review-pending',transformation='New Hinglish instruction adaptation; signatures, helpers and upstream tests retained. Human review of English does not validate this translation.'))
    for i,d in enumerate(rows('math_hi.jsonl')[:50]):
        answer=re.split(r'#{3,4}\s*',d['answer'])[-1].strip().replace(',','')
        tasks.append(dict(id=f'math-{i:03}',type='math',language='hi',prompt=d['question']+'\nकेवल अंतिम संख्या दें।',answer=answer,rationale=d['answer'],source_id='gsm8k-hi',source_item=f'test row {i}',review_status='upstream-human-reviewed',transformation='Question unchanged; appended output-format instruction; final number parsed from upstream answer.'))
    for i,d in enumerate(rows('causal_ta.jsonl')[:50]):
        q='காரணம் என்ன?' if d['question']=='cause' else 'இதன் விளைவு என்ன?'
        prompt=f"{d['premise']}\n{q}\n1. {d['choice1']}\n2. {d['choice2']}\n1 அல்லது 2 மட்டும் பதிலளிக்கவும்."
        tasks.append(dict(id=f'causal-{i:03}',type='causal',language='ta',prompt=prompt,answer=str(d['label']+1),source_id='xcopa',source_item=str(d['idx']),review_status='upstream-human-reviewed',transformation='Premise and choices unchanged; label mapped from zero-based to 1/2; Tamil format instruction appended.'))
    qa=json.loads((upstream/'qa_bn.json').read_text())
    eligible=[d for d in qa['examples'] if all(a['text'] in d['context'] for a in d['answers'])]
    excluded=[{'id':d['id'],'reason':'At least one accepted answer is not a verbatim context span'} for d in qa['examples'] if d not in eligible]
    write_json(ROOT/'data/exclusions.json',excluded)
    for i,d in enumerate(eligible[:50]):
        tasks.append(dict(id=f'reading-{i:03}',type='reading',language='bn',prompt=d['context']+'\n\n'+d['question']+'\nশুধু সংক্ষিপ্ত উত্তর দিন।',answer=d['answers'][0]['text'],accepted_answers=[a['text'] for a in d['answers']],source_id='xquad-in',source_item=d['id'],review_status='upstream-human-reviewed',transformation='Context/question/answers unchanged; appended short-answer instruction.'))
    for t in tasks:
        s=sources[t['source_id']];t['license']=s['license'];t['source_url']=s['url'];t['source_revision']=s['revision']
        t['sha256']=hashlib.sha256(json.dumps(t,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    out=ROOT/'data/tasks.jsonl';out.write_text(''.join(json.dumps(t,ensure_ascii=False)+'\n' for t in tasks))
    write_json(ROOT/'data/manifest.json',{'version':'0.1.0-preview','count':len(tasks),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'canary':qa['canary'],'human_review':'150 source-reviewed; 50 Hinglish adaptations pending independent review','selection':'First 50 source records per stratum; reading selects first 50 with all answers present verbatim in context. Convenience sample; type and language are confounded.'})
    print('Imported',len(tasks),'tasks')
if __name__=='__main__': main()
