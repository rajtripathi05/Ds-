// Headless walk: queue loads -> approve one -> retune -> STP/threshold change, vs LIVE server.
const BASE = "http://127.0.0.1:" + (process.argv[2] || 8781);
const nf = globalThis.fetch.bind(globalThis);
const checks = [];
let d = await (await nf(BASE + "/queue")).json();
checks.push(["queue loads with stats", d.stats && typeof d.stats.stp === "number"]);
checks.push(["queued items carry reason codes", d.queue.every(q => q.reason_code && q.reason)]);
checks.push(["aging present on every row", d.queue.every(q => q.aging_days >= 1)]);
const before = d.stats;
// approve every checks-pass-but-low-conf doc (R8) like a reviewer would
let reviewed = 0;
for (let round = 0; round < 3; round++) {                 // staged learning: gate caps each step
  const r8 = d.queue.filter(q => q.reason_code === "R8_confidence");
  for (const q of r8) {
    await nf(BASE + "/review", { method: "POST", body: JSON.stringify({ set_id: q.set_id, action: "approve", confidence: q.confidence }) });
    reviewed++;
  }
  await nf(BASE + "/retune", { method: "POST", body: "{}" });
  d = await (await nf(BASE + "/queue")).json();
  if (d.stats.stp > before.stp) break;
}
checks.push(["reviews accepted", reviewed > 0]);
checks.push(["retune lowered threshold", d.stats.threshold < before.threshold]);
checks.push(["STP rose after staged learning", d.stats.stp > before.stp]);
const audit = await (await nf(BASE + "/audit")).json();
checks.push(["audit log has human entries with hashes", audit.some(a => a.actor === "human" && a.hash)]);
let ok = true;
for (const [n, p] of checks) { console.log(p ? "✅" : "❌", n); ok &&= p; }
console.log("UI WALK:", ok ? "GREEN" : "RED");
process.exit(ok ? 0 : 1);
