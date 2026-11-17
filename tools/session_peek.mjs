// 为什么现有的不够用：DSH 会话存档是 session.v4.jsonl.zstd（135 MB 压缩），
// 既没有 zstd CLI，也没有官方导出命令；本脚本用 Node 24 内置 zlib zstd 流式解压，
// 只做「逐行统计 + 结构探测」，不把整个会话装进内存。
import fs from 'node:fs';
import zlib from 'node:zlib';
import readline from 'node:readline';

const src = process.argv[2];
const mode = process.argv[3] || 'summary';

const raw = fs.createReadStream(src);
const dec = zlib.createZstdDecompress();
const rl = readline.createInterface({ input: raw.pipe(dec), crlfDelay: Infinity });

let lines = 0, bytes = 0;
const kinds = new Map();
const types = new Map();
const samples = [];

const pushCount = (m, k) => m.set(k, (m.get(k) || 0) + 1);

for await (const line of rl) {
  lines++; bytes += line.length + 1;
  if (!line.trim()) continue;
  let o;
  try { o = JSON.parse(line); } catch { pushCount(kinds, '<unparsable>'); continue; }
  pushCount(kinds, o.kind || o.type || o.role || Object.keys(o).slice(0, 3).join('+'));
  // 记录顶层键形状
  pushCount(types, Object.keys(o).sort().join(','));
  if (samples.length < 3) samples.push(line.slice(0, 600));
}

console.log(JSON.stringify({ path: src, lines, jsonBytes: bytes, kinds: Object.fromEntries(kinds), shapes: Object.fromEntries([...types].slice(0, 30)), samples }, null, 2));
