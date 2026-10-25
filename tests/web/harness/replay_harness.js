const fs = require("fs");
const S = __dirname;
global.requestAnimationFrame = (f) => f();
global.window = { addEventListener() {} };
// Runs the replay script from web/templates/replay.html against a recorded payload with a DOM stub.
// Usage: node tests/web/harness/replay_harness.js   (payload: tests/web/harness/replay-2025-1.json)
const template = fs.readFileSync(`${S}/../../../web/templates/replay.html`, "utf8");
const script = template.split("\n<script>\n")[1].split("\n</script>")[0]
  .replace(/\{\{ page\.layout\.px_per_second \}\}/g, "4").replace(/\{\{ page\.layout\.row_height \}\}/g, "24")
  .replace(/\{\{ page\.layout\.top \}\}/g, "28").replace(/\{\{ page\.layout\.viewport \}\}/g, "960");
global.performance = { now: () => 0 };
const run = (round, moments) => {
  const data = fs.readFileSync(`${S}/replay-${round}.json`, "utf8");
  const el = (extra = {}) => ({ innerHTML: "", textContent: "", attrs: {}, setAttribute(k, v) { this.attrs[k] = v; }, addEventListener() {}, ...extra });
  const handlers = {};
  const slider = el({ value: "0", max: "99999999", addEventListener: (ev, h) => { handlers[ev] = h; } });
  const ids = { "replay-data": el({ textContent: data }), "replay-svg": el(), scene: el(), laps: el(), moving: el(), band: el(), standings: el(), "table-head": el(), "table-hint": el(), time: slider, play: el(), speed: el({ value: "120" }), clock: el() };
  const stage = el({ clientWidth: 1200, dataset: { standingsUrl: "/s", championshipUrl: "/c" } });
  const fetched = [];
  global.document = { getElementById: (id) => ids[id], querySelector: () => stage, querySelectorAll: () => [] };
  global.fetch = (url) => { fetched.push(url); return Promise.resolve({ text: () => Promise.resolve("") }); };
  eval(script);
  console.log(`== round ${round}`);
  for (const [label, seconds] of moments) {
    slider.value = String(seconds * 1000); handlers.input();
    const offset = -Number(ids.scene.attrs.transform.match(/translate\((-?[\d.]+)/)[1]);
    const band = +ids.band.attrs.x + 12 - offset;
    const fill = ids.band.attrs.fill;
    const finish = +[...ids.laps.innerHTML.matchAll(/x1="([\d.]+)"/g)].at(-1)[1] - offset;
    const c = [...ids.moving.innerHTML.matchAll(/<g class="(out)?"><polyline[^>]*\/><circle cx="([\d.]+)" cy="([\d.]+)"[^>]*\/><text class="code"[^>]*>([^<]+)<\/text>(<text class="gap"[^>]*>([^<]+)<\/text>)?(<rect[^>]*\/><text class="badge"[^>]*>IN PIT<\/text>)?/g)]
      .map(m => ({ out: !!m[1], x: +m[2] - offset, rank: Math.round((+m[3] - 28) / 24) + 1, code: m[4], gap: m[6] || "", pit: !!m[7] })).sort((a, b) => a.rank - b.rank);
    const fmt = d => `${d.rank}.${d.code}${d.gap ? "[" + d.gap + "]" : ""}${d.pit ? "[PIT]" : ""}${d.out ? "(out)" : ""}@${d.x.toFixed(0)}`;
    console.log(`${label} t=${seconds}s: band=${band.toFixed(0)} ${fill.includes("cheq") ? "CHEQ" : "grey"} finish=${finish.toFixed(0)} | ${c.slice(0, 3).map(fmt).join(" ")} … ${c.filter(d => ["STR", "TSU"].includes(d.code.slice(0,3))).map(fmt).join(" ")} | table=${fetched.at(-1)}`);
  }
};
run("2025-1", [["start", 0], ["lap1", 60], ["fills", 200], ["mid", 3000], ["NOR finish", 6126.3], ["+1s", 6127.3], ["+60s", 6186]]);
