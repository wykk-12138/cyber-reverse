// 为什么现有的不够用：DSH 会话存档没有导出命令，且 553 MB JSONL 无法整体读入。
// 本脚本流式解压，把事件投影成「精简事件表」，供后续分层切片；不修改任何会话数据。
import fs from 'node:fs';
import zlib from 'node:zlib';
import readline from 'node:readline';

const src = process.argv[2];
const outDir = process.argv[3];

const rl = readline.createInterface({
  input: fs.createReadStream(src).pipe(zlib.createZstdDecompress()),
  crlfDelay: Infinity,
});

const out = {
  events: fs.createWriteStream(outDir + '/events.jsonl'),
  raw: fs.createWriteStream(outDir + '/raw_index.jsonl'),
};

const str = (v, n = 400) => (typeof v === 'string' ? (v.length > n ? v.slice(0, n) + `…[+${v.length - n}]` : v) : v);

function textOf(content) {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) {
    return content.map((c) => {
      if (typeof c === 'string') return c;
      if (c && typeof c === 'object') {
        if (c.type === 'text' || c.type === 'input_text') return c.text ?? '';
        if (c.type === 'tool_result') return `[tool_result ${c.tool_use_id ?? ''}]`;
        if (c.type === 'tool_use') return `[tool_use ${c.name ?? ''}]`;
        return `[${c.type ?? 'obj'}]`;
      }
      return String(c);
    }).join('\n');
  }
  return content == null ? '' : JSON.stringify(content);
}

let seq = 0;
const counts = {};
for await (const line of rl) {
  if (!line.trim()) continue;
  let o;
  try { o = JSON.parse(line); } catch { continue; }
  const t = o.type;
  counts[t] = (counts[t] || 0) + 1;
  const d = o.data || {};
  const base = { i: seq++, t, time: o.time };

  const emit = (extra) => out.events.write(JSON.stringify({ ...base, ...extra }) + '\n');

  switch (t) {
    case 'user/message':
      emit({ kind: 'user', text: str(textOf(d.message?.content ?? d.content ?? d.message ?? d), 200000) });
      break;
    case 'assistant/message': {
      const c = d.message?.content ?? d.content;
      emit({ kind: 'assistant', text: str(textOf(c), 200000) });
      break;
    }
    case 'tool/call': {
      const name = d.name ?? d.toolName ?? d.message?.name ?? '?';
      const args = d.arguments ?? d.input ?? d.args ?? d.message?.input;
      emit({ kind: 'tool_call', name, args: str(typeof args === 'string' ? args : JSON.stringify(args ?? null), 800) });
      break;
    }
    case 'tool/result': {
      const res = d.result ?? d.content ?? d.output ?? d;
      const s = typeof res === 'string' ? res : JSON.stringify(res);
      emit({ kind: 'tool_result', name: d.name ?? d.toolName ?? '', len: s.length, text: str(s, 600) });
      break;
    }
    case 'turn/start':
      emit({ kind: 'turn_start', turnId: d.turnId ?? d.id });
      break;
    case 'turn/end':
      emit({ kind: 'turn_end', turnId: d.turnId ?? d.id, status: d.status });
      break;
    case 'compaction/summary':
      emit({ kind: 'compaction_summary', text: str(textOf(d.summary ?? d.content ?? d.text ?? d), 400000) });
      break;
    case 'compaction/start':
    case 'compaction/end':
      emit({ kind: t.replace('/', '_') });
      break;
    case 'session/title':
      emit({ kind: 'title', text: str(d.title ?? JSON.stringify(d), 2000) });
      break;
    case 'goal/change':
      emit({ kind: 'goal', text: str(JSON.stringify(d), 4000) });
      break;
    case 'deliverables/presented':
      emit({ kind: 'presented', text: str(JSON.stringify(d), 2000) });
      break;
    case 'session/end-seed':
      emit({ kind: 'seed', text: str(JSON.stringify(d), 2000) });
      break;
    default:
      emit({ kind: 'other', text: str(JSON.stringify(d), 400) });
  }
}
out.events.end();
out.raw.end();
console.log(JSON.stringify({ counts }, null, 2));
