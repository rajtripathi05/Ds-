// Headless walk (C6): real UI JS + LIVE server. ask -> cite -> role-flip -> refusal.
import { readFileSync } from "fs";
const BASE = "http://127.0.0.1:" + (process.argv[2] || 8771);
const nativeFetch = globalThis.fetch.bind(globalThis);
function el(id){ const e={id,_html:"",value:"",style:{},
  classList:{_s:new Set(),add(...c){c.forEach(x=>this._s.add(x))},remove(...c){c.forEach(x=>this._s.delete(x))},toggle(){},contains(c){return this._s.has(c)}},
  appendChild(c){ (this._kids??=[]).push(c) }, addEventListener(){},
  set innerHTML(v){this._html=v}, get innerHTML(){return this._html},
  set textContent(v){this._t=v}, get textContent(){return this._t||""},
  set onclick(f){this._onclick=f}, get onclick(){return this._onclick},
  set scrollTop(v){}, get scrollHeight(){return 0}, querySelector(){return el("q")} };
  return e; }
const els={};
const document={getElementById:id=>(els[id]??=el(id)),createElement:t=>el(t)};
const src=readFileSync("ui/index.html","utf8").match(/<script>([\s\S]*?)<\/script>/)[1];
const apiFetch=(p,o)=>nativeFetch(p.startsWith("http")?p:BASE+p,o);
new Function("document","fetch",src)(document, apiFetch);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const checks=[];
// as OPS: policy question
els["q"].value="How many Earned Leave days do employees get per year now?";
await els["send"].onclick(); await sleep(600);
const kids=()=>els["chat"]._kids||[];
let last=kids()[kids().length-1]._kids[0]._html;
checks.push(["ops policy answer cites 2025 policy", /hr-leave-policy-2025/.test(last) && /22 days/.test(last)]);
// as OPS: margin question -> refusal
els["q"].value="What is the distributor margin on Confectionery?";
await els["send"].onclick(); await sleep(600);
last=kids()[kids().length-1]._kids[0]._html;
checks.push(["ops margin refused, no 10% leak", /REFUSE/i.test(last) && !/10%/.test(last)]);
// flip role to EXEC and re-ask
els["rExec"].onclick();
els["q"].value="What is the distributor margin on Confectionery?";
await els["send"].onclick(); await sleep(600);
last=kids()[kids().length-1]._kids[0]._html;
checks.push(["exec same question answers 10% + memo cite", /10%/.test(last) && /fin-margin-structure-memo/.test(last)]);
// numeric ask renders chart + trace
els["q"].value="Why did North-zone Rajnigandha volumes drop in early 2025?";
await els["send"].onclick(); await sleep(900);
last=kids()[kids().length-1]._kids[0]._html;
checks.push(["numeric answer embeds chart img + trace", /<img src="\/out\/charts\//.test(last) && /tool trace/.test(last)]);
let ok=true;
for(const [n,p] of checks){ console.log(p?"✅":"❌", n); ok&&=p; }
console.log("UI WALK:", ok?"GREEN":"RED");
process.exit(ok?0:1);
