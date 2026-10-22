#!/usr/bin/env node
// launch_check.js — read-only pre-check of an app's declared launch, run by grade_setup.sh
// after the install.
//
//   node launch_check.js <project root> [<app root>] [<script name, default dev>]
//
// It follows `npm run <script>` at the project root through every command it runs (the
// scripts it calls with `npm run`, the commands `concurrently` starts, `cd`), and reports
// what will stop the launch before anything runs:
//   - a command that is neither installed in node_modules/.bin (the package's folder or a
//     folder above it, as npm searches) nor a system command: `sh: X: not found`;
//   - `npx X` with X not installed: npx would fetch it from the registry;
//   - `node <file>` naming a file that does not exist;
//   - `vite` (dev server) started in a folder with no index.html and no vite.config.*: it
//     serves no page (404 at /).
// It never runs anything, and it decides nothing: L1 and L2 are judged by running the
// declared command (rubric README). It only tells the grader what to expect.
//
// Output: one line per finding, "WARN<TAB>text" or "INFO<TAB>text", then "DONE<TAB>n".
"use strict";
const fs = require("fs");
const path = require("path");

const projectRoot = path.resolve(process.argv[2] || ".");
const appRoot = path.resolve(process.argv[3] || projectRoot);
const startScript = process.argv[4] || "dev";

const rel = (p) => {
  const r = path.relative(appRoot, p);
  return r === "" ? "./" : r + "/";
};
const out = [];
const seen = new Set();

// System commands: on PATH, but not the Node install's own bin folder (a global package
// there would hide one the app forgot to declare), except Node's own tools.
const nodeBin = path.dirname(process.execPath);
const globalBin = process.env.NPM_GLOBAL_BIN ? path.resolve(process.env.NPM_GLOBAL_BIN) : null;
const NODE_TOOLS = new Set(["node", "npm", "npx", "corepack"]);
const BUILTINS = new Set(["cd", "echo", "exit", "true", "false", "export", "set", "test", "[",
  "wait", "sleep", "kill", "trap", "exec", "eval", "source", ".", ":", "unset", "read", "printf"]);
function onSystemPath(cmd) {
  if (BUILTINS.has(cmd)) return true;
  for (const d of (process.env.PATH || "").split(path.delimiter)) {
    if (!d) continue;
    const rd = path.resolve(d);
    if ((rd === nodeBin || rd === globalBin) && !NODE_TOOLS.has(cmd)) continue;
    try { fs.accessSync(path.join(d, cmd), fs.constants.X_OK); return true; } catch {}
  }
  return false;
}
// npm puts node_modules/.bin of the package folder and of every folder above it on PATH.
function inBin(pkgDir, cmd) {
  let d = pkgDir;
  for (;;) {
    if (fs.existsSync(path.join(d, "node_modules", ".bin", cmd))) return true;
    const up = path.dirname(d);
    if (d === appRoot || up === d || !(up + path.sep).startsWith(appRoot + path.sep) && up !== appRoot) return false;
    d = up;
  }
}
// Is a package named `name` declared by the package.json of pkgDir or of a folder above it?
function declared(pkgDir, name) {
  let d = pkgDir;
  for (;;) {
    try {
      const p = JSON.parse(fs.readFileSync(path.join(d, "package.json"), "utf8"));
      for (const k of ["dependencies", "devDependencies", "optionalDependencies"])
        if (p[k] && name in p[k]) return rel(d) + "package.json";
    } catch {}
    if (d === appRoot) return null;
    const up = path.dirname(d);
    if (up === d || !(up + path.sep).startsWith(appRoot + path.sep) && up !== appRoot) return null;
    d = up;
  }
}
function findPkgDir(dir) {
  let d = dir;
  for (;;) {
    if (fs.existsSync(path.join(d, "package.json"))) return d;
    const up = path.dirname(d);
    if (up === d) return null;
    d = up;
  }
}
function readScripts(pkgDir) {
  try { return JSON.parse(fs.readFileSync(path.join(pkgDir, "package.json"), "utf8")).scripts || {}; }
  catch { return null; }
}

// A small shell tokenizer: words, quotes, and the operators && || ; | &.
function tokenize(s) {
  const toks = [];
  let cur = null, q = null;
  const push = () => { if (cur !== null) { toks.push(cur); cur = null; } };
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (q) {
      if (c === q) { q = null; continue; }
      if (c === "\\" && q === '"' && i + 1 < s.length) { cur.v += s[++i]; continue; }
      cur.v += c; continue;
    }
    if (c === "'" || c === '"') { if (cur === null) cur = { v: "", quoted: true }; else cur.quoted = true; q = c; continue; }
    if (/\s/.test(c)) { push(); continue; }
    const two = s.slice(i, i + 2);
    if (two === "&&" || two === "||") { push(); toks.push({ op: two }); i++; continue; }
    if (c === ";" || c === "|" || c === "&") { push(); toks.push({ op: c }); continue; }
    if (cur === null) cur = { v: "", quoted: false };
    cur.v += c;
  }
  push();
  return toks;
}

function runScript(pkgDir, name, via) {
  const key = pkgDir + "\0" + name;
  if (seen.has(key)) return;
  seen.add(key);
  const scripts = readScripts(pkgDir);
  if (!scripts) { out.push(["WARN", `${via}: ${rel(pkgDir)}package.json cannot be read or is not valid JSON`]); return; }
  if (!(name in scripts)) { out.push(["WARN", `${via}: ${rel(pkgDir)}package.json has no "${name}" script (npm: Missing script)`]); return; }
  runCommandLine(scripts[name], pkgDir, pkgDir, `npm run ${name} in ${rel(pkgDir)}`);
}

function runCommandLine(line, cwd0, pkgDir, via) {
  const toks = tokenize(line);
  let cwd = cwd0, seg = [];
  const flush = () => { if (seg.length) cwd = runSegment(seg, cwd, pkgDir, via); seg = []; };
  for (const t of toks) { if (t.op) flush(); else seg.push(t); }
  flush();
}

// Returns the cwd after the segment (only `cd` changes it).
function runSegment(seg, cwd, pkgDir, via) {
  let i = 0;
  while (i < seg.length && /^[A-Za-z_][A-Za-z0-9_]*=/.test(seg[i].v) && !seg[i].quoted) i++;
  if (i >= seg.length) return cwd;
  const cmd = seg[i].v, args = seg.slice(i + 1).map((t) => t.v), raw = seg.slice(i + 1);
  if (cmd === "cd") {
    const to = args[0] ? path.resolve(cwd, args[0]) : cwd;
    if (!fs.existsSync(to)) out.push(["WARN", `${via}: cd ${args[0]}: no such folder in ${rel(cwd)}`]);
    return to;
  }
  if (cmd === "npm" || cmd === "pnpm" || cmd === "yarn") {
    if (cmd !== "npm") { if (!onSystemPath(cmd)) out.push(["WARN", `${via}: ${cmd} is not installed (sh: ${cmd}: not found)`]); return cwd; }
    let prefix = null, sub = null, name = null;
    for (let k = 0; k < args.length; k++) {
      const a = args[k];
      if (a === "--prefix" || a === "-C") { prefix = args[++k]; continue; }
      if (a.startsWith("--prefix=")) { prefix = a.slice(9); continue; }
      if (a.startsWith("-")) continue;
      if (sub === null) { sub = a; continue; }
      if (name === null) { name = a; }
    }
    let target = cwd;
    if (prefix) {
      target = path.resolve(cwd, prefix);
      if (!fs.existsSync(path.join(target, "package.json"))) {
        out.push(["WARN", `${via}: npm --prefix ${prefix}: no package.json in ${rel(target)}`]);
        return cwd;
      }
    }
    if (sub === "run" || sub === "run-script" || sub === "rum" || sub === "urn") {
      if (!name) return cwd;
      const pd = findPkgDir(target);
      if (!pd) out.push(["WARN", `${via}: npm run ${name}: no package.json in or above ${rel(target)}`]);
      else runScript(pd, name, via);
    } else if (sub === "start" || sub === "test") {
      const pd = findPkgDir(target);
      const sc = pd && readScripts(pd);
      if (sc && sub in sc) runScript(pd, sub, via);
      else if (sub === "start" && pd && !fs.existsSync(path.join(pd, "server.js")))
        out.push(["WARN", `${via}: npm start: ${rel(pd)}package.json has no "start" script and no server.js`]);
    }
    return cwd;
  }
  if (cmd === "npx") {
    let k = 0;
    while (k < args.length && args[k].startsWith("-")) k++;
    const tool = args[k];
    if (tool && !inBin(pkgDir, tool) && !inBin(cwd, tool) && !onSystemPath(tool))
      out.push(["WARN", `${via}: npx ${tool}: not installed in the app, so npx would fetch it from the registry`]);
    if (tool === "vite") checkVite(args.slice(k + 1), cwd, via);
    return cwd;
  }
  if (cmd === "node" || cmd === "nodejs") {
    const takesValue = new Set(["-r", "--require", "--import", "--loader", "--experimental-loader", "--env-file", "--conditions", "-C"]);
    for (let k = 0; k < args.length; k++) {
      const a = args[k];
      if (a === "-e" || a === "--eval" || a === "-p" || a === "--print" || a === "-") return cwd;
      if (takesValue.has(a)) { k++; continue; }
      if (a.startsWith("-")) continue;
      const f = path.resolve(cwd, a);
      const exists = fs.existsSync(f) || [".js", ".mjs", ".cjs"].some((x) => fs.existsSync(f + x))
        || fs.existsSync(path.join(f, "index.js"));
      if (!exists) out.push(["WARN", `${via}: node ${a}: no such file in ${rel(cwd)} (Cannot find module)`]);
      return cwd;
    }
    return cwd;
  }
  // Any other command: installed in node_modules/.bin, or a system command.
  if (!inBin(pkgDir, cmd) && !onSystemPath(cmd)) {
    const by = declared(pkgDir, cmd);
    out.push(["WARN", `${via}: ${cmd} is not installed (no node_modules/.bin/${cmd} in ${rel(pkgDir)} or above; `
      + (by ? `${by} declares it, so its install has not finished` : `no package.json of the app declares it`)
      + `): sh: ${cmd}: not found`]);
    if (cmd !== "concurrently") return cwd;   // its commands are still followed, for the accommodations
  }
  if (cmd === "concurrently") {
    const takesValue = new Set(["-n", "--names", "-c", "--prefix-colors", "-p", "--prefix", "-k", "--kill-signal",
      "-s", "--success", "--max-processes", "-m", "--name-separator", "--timestamp-format", "-t", "-l", "--prefix-length",
      "--restart-tries", "--restart-after", "--handle-input", "--default-input-target", "-P", "--passthrough-arguments"]);
    const flagOnly = new Set(["-k", "--kill-others", "--kill-others-on-fail", "-r", "--raw", "--no-color", "-g", "--group",
      "--hide", "-i", "--handle-input", "--timings", "--passthrough-arguments", "-P"]);
    for (let k = 0; k < raw.length; k++) {
      const a = raw[k].v;
      if (!raw[k].quoted && a.startsWith("-")) {
        if (a.includes("=") || flagOnly.has(a)) continue;
        if (takesValue.has(a)) k++;
        continue;
      }
      if (a.startsWith("npm:")) { const n = a.slice(4); if (!n.includes("*")) runScript(findPkgDir(cwd) || pkgDir, n, via); continue; }
      runCommandLine(a, cwd, pkgDir, via);
    }
    return cwd;
  }
  if (cmd === "vite") checkVite(args, cwd, via);
  return cwd;
}

function checkVite(args, cwd, via) {
  const first = args.find((a) => !a.startsWith("-"));
  if (first && first !== "dev" && first !== "serve") return;          // build, preview, or a root folder
  if (args.some((a) => a === "--config" || a === "-c" || a.startsWith("--config="))) return;
  const configs = ["vite.config.js", "vite.config.ts", "vite.config.mjs", "vite.config.cjs", "vite.config.mts", "vite.config.cts"];
  if (configs.some((c) => fs.existsSync(path.join(cwd, c)))) return;    // its config may set the root
  if (fs.existsSync(path.join(cwd, "index.html"))) return;
  const elsewhere = [];
  for (const d of fs.readdirSync(cwd, { withFileTypes: true })) {
    if (d.isDirectory() && d.name !== "node_modules" && !d.name.startsWith(".")
        && (fs.existsSync(path.join(cwd, d.name, "index.html")) || configs.some((c) => fs.existsSync(path.join(cwd, d.name, c)))))
      elsewhere.push(d.name + "/");
  }
  out.push(["WARN", `${via}: vite starts in ${rel(cwd)}, which has no index.html and no vite.config.*, so it serves no page (404 at /)`
    + (elsewhere.length ? `; the page and its config are in ${elsewhere.join(", ")}` : "")]);
}

const pd = findPkgDir(projectRoot);
if (!pd) out.push(["INFO", `no package.json at the project root ${rel(projectRoot)}`]);
else {
  const sc = readScripts(pd);
  if (sc && !(startScript in sc)) out.push(["INFO", `no "${startScript}" script at the project root (README, "No root dev script")`]);
  else runScript(pd, startScript, `npm run ${startScript}`);
}
const seenText = new Set();
let n = 0;
for (const [t, text] of out) {
  if (seenText.has(text)) continue;
  seenText.add(text);
  if (t === "WARN") n++;
  console.log(`${t}\t${text}`);
}
console.log(`DONE\t${n}`);
