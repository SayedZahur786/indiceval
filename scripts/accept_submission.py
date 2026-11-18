"""Maintainer tool: regrade reviewed evidence and add a traceable leaderboard row."""
import argparse,json,shutil
from pathlib import Path
from indiceval.runner import validate_bundle
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('directory')
p.add_argument('--review-url',required=True,help='Public GitHub review with disclosure and acceptance')
args=p.parse_args()
if not args.review_url.startswith('https://github.com/SayedZahur786/indiceval/'):
    p.error('Review must be in the project repository')
src=Path(args.directory)
report=validate_bundle(src,submission=True)
meta=json.loads((src/'run.json').read_text())
run_id=meta['id']
if not run_id.isalnum():p.error('Invalid run ID')
destination=ROOT/'results'/run_id
if destination.exists():p.error('Run already imported')
destination.mkdir(parents=True)
for name in ['run.json','samples.jsonl','report.json']:
    shutil.copyfile(src/name,destination/name)
row=dict(report,model=meta['model'],run_id=run_id,dataset_sha256=meta['dataset_sha256'],
         evidence_url='https://github.com/SayedZahur786/indiceval/tree/main/results/'+run_id,
         review_url=args.review_url)
board=ROOT/'site/data/leaderboard.json'
rows=json.loads(board.read_text())
if any(r['dataset_sha256']!=row['dataset_sha256'] for r in rows):
    p.error('Cannot combine dataset versions in one ranking')
rows.append(row);rows.sort(key=lambda r:r['accuracy'],reverse=True)
board.write_text(json.dumps(rows,indent=2)+'\n')
print('Imported reviewed run',run_id,'; inspect diff before committing.')
