// 读一段已知偏移的字节上下文：binstr.mjs 只报命中点，判断「根级 mcp_config.json 是否被读」
// 需要看完整编号列表，PowerShell 无法精确 seek 二进制。
// 用法: node dump.mjs <file> <offset> <length>
import { open } from 'node:fs/promises';

const [, , file, offArg, lenArg] = process.argv;
const off = Number(offArg);
const len = Number(lenArg ?? 2000);
const fh = await open(file, 'r');
const buf = Buffer.alloc(len);
const { bytesRead } = await fh.read(buf, 0, len, off);
await fh.close();
console.log(`--- 0x${off.toString(16)} len=${bytesRead}`);
console.log(buf.subarray(0, bytesRead).toString('latin1').replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g, '.'));
