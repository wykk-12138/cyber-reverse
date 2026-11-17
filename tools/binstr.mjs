// 为什么不用 rg/grep：Antigravity 的 agent 是 Go 打包的 215MB 单文件，
// 需要精确的字节偏移 + 上下文窗口来判断「工作区级 mcp_config.json 是否被读取」，
// PowerShell 的 Select-String 对二进制会截断行且丢失偏移，rg 会跳过二进制。
// 用法: node binstr.mjs <file> <needle> [ctxBytes] [maxHits]
import { open } from 'node:fs/promises';

const [, , file, needle, ctxArg, maxArg] = process.argv;
if (!file || !needle) {
  console.error('usage: node binstr.mjs <file> <needle> [ctxBytes] [maxHits]');
  process.exit(2);
}
const ctx = Number(ctxArg ?? 160);
const maxHits = Number(maxArg ?? 40);

const fh = await open(file, 'r');
const { size } = await fh.stat();
const CHUNK = 8 * 1024 * 1024;
const nb = Buffer.from(needle, 'latin1');
const nc = Buffer.from(needle, 'utf16le');
let buf = Buffer.alloc(0);
let base = 0;
let hits = 0;
const results = [];

function scan(block, blockBase) {
  for (const [tag, n] of [['ascii', nb], ['utf16', nc]]) {
    let i = block.indexOf(n);
    while (i !== -1) {
      const pos = blockBase + i;
      const s = Math.max(0, i - ctx);
      const e = Math.min(block.length, i + n.length + ctx);
      results.push({
        off: pos,
        enc: tag,
        ctx: block.slice(s, e).toString('latin1').replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g, '.'),
      });
      hits++;
      if (hits >= maxHits) return true;
      i = block.indexOf(n, i + 1);
    }
  }
  return false;
}

let pos = 0;
let done = false;
while (pos < size && !done) {
  const len = Math.min(CHUNK, size - pos);
  buf = Buffer.alloc(len + nb.length + nc.length);
  const { bytesRead } = await fh.read(buf, 0, len, pos);
  buf = buf.subarray(0, bytesRead);
  done = scan(buf, pos);
  pos += bytesRead;
  if (bytesRead === 0) break;
}
await fh.close();

console.log(`file=${file} size=${size} needle=${JSON.stringify(needle)} hits=${hits}${hits >= maxHits ? ' (capped)' : ''}`);
for (const r of results) {
  console.log(`\n--- off=0x${r.off.toString(16)} (${r.off}) enc=${r.enc}`);
  console.log(r.ctx);
}
