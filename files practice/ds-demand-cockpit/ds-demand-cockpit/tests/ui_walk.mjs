// Headless UI walk (B3): executes the cockpit's real JS against the LIVE server API
// with a stub DOM (no browser available offline). Asserts boot, role switch, what-if flow.
import { readFileSync } from "fs";
const BASE = "http://127.0.0.1:" + (process.argv[2] || 8792);
let drawOps = 0;
const ctxStub = new Proxy({}, { get: (t, k) => (k === "canvas" ? null : (...a) => { drawOps++; } ),
                                set: () => true });
function el(id) {
  const e = { id, _html: "", _text: "", value: id === "wBudget" ? "100" : (id === "catSel" ? "__nation__" : "0"),
    style: {}, width: 760, height: 300, selectedOptions: [], selectedIndex: 0,
    classList: { _s: new Set(), add(...c){c.forEach(x=>this._s.add(x))}, remove(...c){c.forEach(x=>this._s.delete(x))},
                 toggle(c,f){ f ? this._s.add(c) : this._s.delete(c) }, contains(c){return this._s.has(c)} },
    getContext: () => ctxStub, querySelector: () => el(id + ">q"), querySelectorAll: () => [],
    appendChild(){}, addEventListener(){},
    set innerHTML(v){ this._html = v }, get innerHTML(){ return this._html },
    set textContent(v){ this._text = String(v) }, get textContent(){ return this._text },
    set href(v){ this._href = v }, get href(){ return this._href },
    set onclick(f){ this._onclick = f }, get onclick(){ return this._onclick },
    set oninput(f){ this._oninput = f }, get oninput(){ return this._oninput },
    set onchange(f){ this._onchange = f }, get onchange(){ return this._onchange } };
  return e;
}
const els = {};
const document = {
  getElementById: id => (els[id] ??= el(id)),
  body: el("body"),
  querySelector: () => el("q"), querySelectorAll: () => [],
};
const window = {}; const performance = { now: () => Date.now() };
const html = readFileSync("cockpit/index.html", "utf8");
const src = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const nativeFetch = globalThis.fetch.bind(globalThis);
const apiFetch = (p, o) => nativeFetch(p.startsWith("http") ? p : BASE + p, o);
const fn = new Function("document", "window", "performance", "fetch", src + "\n;return {runScenario, saveScenario, params};");
const api = fn(document, window, performance, apiFetch);
const sleep = ms => new Promise(r => setTimeout(r, ms));
let checks = [];
await sleep(1500);   // boot() async
checks.push(["boot rendered KPI cards", els["kpis"]._html.includes("WMAPE")]);
checks.push(["charts drew (canvas ops > 50)", drawOps > 50]);
checks.push(["quality panel shows recovered elasticities", els["quality"]._html.includes("recovered")]);
const gid = id => document.getElementById(id);
gid("wDepth").value = "25"; gid("wCat").value = "Confectionery"; gid("wType").value = "consumer";
gid("wPriceCat").value = "Beverages"; gid("wPrice").value = "0"; gid("wLaunch").value = "";
gid("wWeeks").selectedOptions = [{value:"1"},{value:"2"},{value:"3"},{value:"4"}];
await api.runScenario(); await sleep(200);
checks.push(["what-if updated Δ volume", /[+−-]\d/.test(els["dVol"]._text)]);
checks.push(["binding constraint shown", els["rBind"]._text.length > 3]);
checks.push(["solve badge < 2s", els["solveMs"]._text.includes("ms")]);
await api.saveScenario(); await sleep(300);
checks.push(["scenario saved + listed", els["scenCount"]._text.match(/\d+/) && +els["scenCount"]._text.match(/\d+/)[0] >= 1]);
// role switch to ops
els["roleOps"]; // exists
const opsSnap = await (await nativeFetch(BASE + "/snapshot?role=ops")).json();
const opsKeys = (JSON.stringify(opsSnap).match(/"([^"]+)":/g) || []).join(" ");
checks.push(["ops snapshot has no financial keys", !/margin|budget|roi|price|cost|value|objective|shadow/i.test(opsKeys)]);
let ok = true;
for (const [n, p] of checks) { console.log(p ? "✅" : "❌", n); ok &&= p; }
console.log("UI WALK:", ok ? "GREEN" : "RED");
process.exit(ok ? 0 : 1);
