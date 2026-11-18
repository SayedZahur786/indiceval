'use strict';
const $=id=>document.getElementById(id);
const names={code:'Code generation',math:'Math reasoning',causal:'Causal reasoning',reading:'Reading comprehension'};
const langs={'hi-Latn':'Hinglish',hi:'Hindi',ta:'Tamil',bn:'Bengali'};
let tasks=[],filtered=[],page=0;
const size=6;
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n}
function render(){
 filtered=tasks.filter(t=>(!$('type').value||t.type===$('type').value)&&(!$('language').value||t.language===$('language').value)&&[t.prompt,t.id,t.source_id].join(' ').toLowerCase().includes($('search').value.toLowerCase()));
 const pages=Math.max(1,Math.ceil(filtered.length/size));page=Math.min(page,pages-1);
 $('result-count').textContent=filtered.length+' of '+tasks.length+' tasks';
 $('page-count').textContent='Page '+(page+1)+' of '+pages;
 $('previous').disabled=page===0;$('next').disabled=page>=pages-1;
 $('tasks').replaceChildren();
 if(!filtered.length)$('tasks').append(el('p','No tasks match these filters. Try another language or reset the filters.'));
 for(const t of filtered.slice(page*size,(page+1)*size)){
  const card=el('article',undefined,'task-card'),meta=el('div',undefined,'card-meta');
  meta.append(el('span',t.id),el('span',langs[t.language]));card.append(meta,el('h3',names[t.type]),el('p',t.prompt));
  const foot=el('div',undefined,'card-foot'),pending=t.review_status.includes('pending');
  foot.append(el('span',pending?'Adaptation review pending':'Upstream human review','review-label'+(pending?' pending':'')));
  const b=el('button','Inspect task');b.setAttribute('aria-label','Inspect '+t.id);b.onclick=()=>openTask(t);foot.append(b);card.append(foot);$('tasks').append(card);
 }
}
function openTask(t){
 $('dialog-id').textContent=t.id;$('dialog-title').textContent=names[t.type]+' · '+langs[t.language];
 $('dialog-meta').textContent=t.source_id+' / '+t.source_item+' / '+t.license;
 $('dialog-prompt').textContent=t.prompt;$('dialog-answer').textContent=t.answer;
 $('dialog-tests').textContent=t.tests||t.rationale||('Accepted answers: '+(t.accepted_answers||[t.answer]).join(' · '));
 $('dialog-review').textContent=t.review_status==='adaptation-review-pending'?'The English source problem was human-written. This new Hinglish adaptation has not received independent human language review.':'The source documents human translation/review. This project checked source fidelity and reference scoring; it has not independently repeated human annotation.';
 $('dialog-transformation').textContent=t.transformation;$('dialog-source').href=t.source_url;
 $('dialog-hash').textContent='Task SHA-256: '+t.sha256;
 $('dialog-issue').href='https://github.com/SayedZahur786/indiceval/issues/new?template=task.yml&title='+encodeURIComponent('Task review: '+t.id);
 $('answer-details').open=false;$('task-dialog').showModal();
}
$('close-dialog').onclick=()=>$('task-dialog').close();
$('task-dialog').addEventListener('click',e=>{if(e.target===$('task-dialog')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close()}});
for(const id of ['search','type','language'])$(id).addEventListener('input',()=>{page=0;render()});
$('reset').onclick=()=>{for(const id of ['search','type','language'])$(id).value='';page=0;render()};
$('previous').onclick=()=>{page--;render()};$('next').onclick=()=>{page++;render()};
$('copy').onclick=async()=>{try{await navigator.clipboard.writeText($('setup-command').textContent);$('copy').textContent='Copied'}catch{$('copy').textContent='Select and copy below'}};
$('report-file').addEventListener('change',async e=>{
 const file=e.target.files[0];if(!file)return;
 try{
  if(file.size>2_000_000)throw Error('Report exceeds 2 MB.');
  const r=JSON.parse(await file.text());
  for(const k of ['accuracy','tasks','repeats','latency_p50_s','cost_coverage'])if(typeof r[k]!=='number'||!Number.isFinite(r[k])||r[k]<0)throw Error('Not an IndicEval report: invalid '+k);
  if(r.accuracy>1||r.cost_coverage>1||r.tasks<1||r.repeats<1)throw Error('Invalid report range.');
  for(const k of ['score_variance','cost_per_task_usd'])if(r[k]!==null&&(typeof r[k]!=='number'||!Number.isFinite(r[k])||r[k]<0))throw Error('Invalid '+k);
  const grid=el('div',undefined,'report-metrics');
  for(const [label,value] of [['Accuracy',(r.accuracy*100).toFixed(1)+'%'],['Sample variance',r.score_variance===null?'Not available':r.score_variance.toFixed(6)],['Cost / task',r.cost_per_task_usd===null?'Unknown':'$'+r.cost_per_task_usd.toFixed(6)],['Latency p50',r.latency_p50_s.toFixed(3)+' s']]){
   const box=el('div');box.append(el('strong',value),el('span',label));grid.append(box);
  }
  $('report-view').replaceChildren(grid);
  $('report-status').className='';$('report-status').textContent=r.tasks+' tasks · '+r.repeats+' repetitions · '+(r.cost_coverage*100).toFixed(0)+'% cost coverage. Local display only; this does not verify or submit the run.';
 }catch(err){$('report-status').className='error';$('report-status').textContent='Could not open report: '+err.message}
});
fetch('/data/tasks.jsonl').then(r=>{if(!r.ok)throw Error('Task download failed');return r.text()}).then(text=>{tasks=text.trim().split('\n').map(JSON.parse);render()}).catch(()=>{$('result-count').textContent='Unable to load tasks. Reload or download the dataset from GitHub.'});
fetch('/data/leaderboard.json').then(r=>r.json()).then(data=>{
 $('submission-count').textContent=data.length+' accepted runs';
 if(data.length)$('empty-board').hidden=true;
 for(const row of data){
  const tr=el('tr');
  const modelCell=el('td'),link=el('a',row.model);link.href=row.evidence_url;modelCell.append(link);tr.append(modelCell);
  for(const value of [(row.accuracy*100).toFixed(1)+'%',(row.pass_at_k['1']*100).toFixed(1)+'%',row.cost_per_task_usd===null?'Unknown':'$'+row.cost_per_task_usd.toFixed(5),row.latency_p50_s.toFixed(2)+' s',row.score_variance.toFixed(6)])tr.append(el('td',value));
  $('ranking').append(tr);
 }
}).catch(()=>{$('submission-count').textContent='Results unavailable'});
