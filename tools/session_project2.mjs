// 为什么现有的不够用：无导出命令 + 553MB JSONL。v2 精确投影：assistant 只取 text 块，
// 用户消息分类去重，工具调用保留 name+参数摘要，压缩摘要全量落盘供人工/ agent 分层阅读。
import fs from 'node:fs';
import zlib from 'node:zlib';
import readline from 'node:readline';

const src = process.argv[2];
const outDir = process.argv[3];
const rl = readline.createInterface({
  input: fs.createReadStream(src).pipe(zlib.createZstdDecompress()),
  crlfDelay: Infinity,
});

const fTimeline = fs.createWriteStream(outDir + '/timeline.jsonl');
const fComp = fs.createWriteStream(outDir + '/compactions.jsonl');

const clip = (s, n) => (s.length > n ? s.slice(0, n) + `…[+${s.length - n} chars]` : s);

let turn = 0, idx = 0;
const stats = { userMsgs: 0, userDup: 0, assistantText: 0, toolCalls: 0, compactions: 0, compBytes: 0 };
const seenUser = new Set();
const lastUserByTurn = new Map();

for await (const line of rl) {
  if (!line.trim()) continue;
  let o; try { o = JSON.parse(line); } catch { continue; }
  const d = o.data || {};
  const t = o.type;

  if (t === 'turn/start') { turn = d.turn ?? turn + 1; continue; }

  switch (t) {
    case 'user/message': {
      const c = d.message?.content;
      let txt = '';
      if (typeof c === 'string') txt = c;
      else if (Array.isArray(c)) txt = c.map((b) => (typeof b === 'string' ? b : b?.type === 'text' ? b.text ?? '' : `[${b?.type}]`)).join('\n');
      stats.userMsgs++;
      const tn = d.turn ?? turn;
      const key = tn + '|' + txt.slice(0, 200);
      if (seenUser.has(key)) { stats.userDup++; break; }
      seenUser.add(key);
      fTimeline.write(JSON.stringify({ i: idx++, t: 'user', turn: tn, time: o.time, len: txt.length, text: clip(txt, 6000) }) + '\n');
      break;
    }
    case 'assistant/message': {
      const c = d.message?.content;
      if (!Array.isArray(c)) break;
      const texts = c.filter((b) => b?.type === 'text' && b.text && b.text.trim()).map((b) => b.text);
      if (texts.length) {
        stats.assistantText++;
        fTimeline.write(JSON.stringify({ i: idx++, t: 'asst', turn: d.turn ?? turn, time: o.time, len: texts.join('\n').length, text: clip(texts.join('\n'), 8000) }) + '\n');
      }
      break;
    }
    case 'tool/call': {
      stats.toolCalls++;
      const name = d.name ?? '?';
      let a = d.arguments;
      if (typeof a !== 'string') a = JSON.stringify(a ?? null);
      fTimeline.write(JSON.stringify({ i: idx++, t: 'call', turn: d.turn ?? turn, name, args: clip(a, 500) }) + '\n');
      break;
    }
    case 'compaction/summary': {
      const s = Array.isArray(d.summary) ? d.summary.map((b) => b?.text ?? '').join('\n') : String(d.summary ?? '');
      stats.compactions++; stats.compBytes += s.length;
      fComp.write(JSON.stringify({ i: stats.compactions, time: o.time, turn, len: s.length, text: s }) + '\n');
      fTimeline.write(JSON.stringify({ i: idx++, t: 'compaction', time: o.time, turn, len: s.length }) + '\n');
      break;
    }
    case 'goal/change': {
      const g = d.goal || {};
      fTimeline.write(JSON.stringify({ i: idx++, t: 'goal', time: o.time, turn, op: d.operation, rev: g.revision, objective: clip(String(g.objective ?? ''), 3000), maxRounds: g.maxRounds ?? g.max_goal_rounds }) + '\n');
      break;
    }
    case 'session/title':
      fTimeline.write(JSON.stringify({ i: idx++, t: 'title', text: String(d.title ?? '') }) + '\n');
      break;
    case 'deliverables/presented':
      fTimeline.write(JSON.stringify({ i: idx++, t: 'presented', turn: d.turn, files: (d.files || []).map((x) => x.path) }) + '\n');
      break;
    case 'todo/write':
      fTimeline.write(JSON.stringify({ i: idx++, t: 'todo', turn: d.turn, len: JSON.stringify(d).length }) + '\n');
      break;
    case 'workspace/changes':
      fTimeline.write(JSON.stringify({ i: idx++, t: 'changes', turn: d.turn, n: (d.changes || []).length }) + '\n');
      break;
    default: break;
  }
}
fTimeline.end(); fComp.end();
console.log(JSON.stringify({ ...stats, turns: turn }, null, 2));
