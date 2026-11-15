// Probe the cua-driver MCP server over stdio: initialize + tools/list.
// Prints the negotiated server info and the tool names it exposes.
const { spawn } = require('child_process');

const exe = process.env.CUA_EXE;
if (!exe) { console.error('CUA_EXE not set'); process.exit(2); }

const child = spawn(exe, ['mcp'], { stdio: ['pipe', 'pipe', 'pipe'] });

let buf = '';
const seen = { init: null, tools: null };
let finished = false;

function send(obj) {
  child.stdin.write(JSON.stringify(obj) + '\n');
}

child.stdout.on('data', (chunk) => {
  buf += chunk.toString('utf8');
  let idx;
  while ((idx = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, idx).trim();
    buf = buf.slice(idx + 1);
    if (!line) continue;

    let msg;
    try { msg = JSON.parse(line); } catch { continue; }

    if (msg.id === 1 && msg.result) {
      seen.init = msg.result;
      // ask for the tool catalogue once the handshake lands
      send({ jsonrpc: '2.0', id: 2, method: 'tools/list', params: {} });
    } else if (msg.id === 2 && msg.result) {
      seen.tools = (msg.result.tools || []).map(t => t.name);
      done(0);
    } else if (msg.error) {
      console.error('server error:', JSON.stringify(msg.error));
      done(3);
    }
  }
});

child.stderr.on('data', (d) => {
  const s = d.toString().trim();
  if (s) console.error('[stderr]', s.slice(0, 300));
});

function done(code) {
  if (finished) return;
  finished = true;
  console.log('=== initialize ===');
  console.log(JSON.stringify({
    serverInfo: seen.init?.serverInfo,
    protocolVersion: seen.init?.protocolVersion,
    capabilities: Object.keys(seen.init?.capabilities || {}),
  }, null, 2));
  console.log('=== tools ===');
  console.log(JSON.stringify(seen.tools, null, 2));
  try { child.kill(); } catch {}
  process.exit(code);
}

const timer = setTimeout(() => {
  console.error('timed out waiting for the MCP handshake');
  done(4);
}, 30000);
timer.unref();

send({
  jsonrpc: '2.0',
  id: 1,
  method: 'initialize',
  params: {
    protocolVersion: '2024-11-05',
    capabilities: {},
    clientInfo: { name: 'dsh-probe', version: '1.0.0' },
  },
});
send({ jsonrpc: '2.0', method: 'notifications/initialized', params: {} });
