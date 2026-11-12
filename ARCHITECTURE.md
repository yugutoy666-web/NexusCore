# Nexus Core — Architecture

> An agent framework where **the filesystem is the body** and the session is only the mouth and ears.
> Model providers are replaceable workers; tools, safety and self-healing stay yours.
> This document is the desensitized (L1–L9) architecture reference for open-sourcing.

## L0 · Ontology (graph-theoretic, v6)

```
Node / Label      unique identifier, primary key — the absolute coordinate
Edge / Path       inheritance / lineage / causal flow — boolean connectivity × float weight
Entity / Subgraph aggregate of internal relation edges; Area = compute-equivalent
App / Collection  external boundary container (files + resources + config)
Agent / Process   the running worker; process death → dead data
Constraints: ID unique · path deadlock-free · entity stream unblocked · app boundary contained · process unstalled
```

---

## L1 · Positions (a fleet, not a box)

```
phone (Android)          primary seat: holds the World, organ app, WebDAV drive
home-server (Linux)      compute node: systemd-resident platform, mirrors, keepalive
windows-node (Win+GPU)   idle compute: SSH-restricted shell, tunnel-based access
owner's drive (ReFS)     the human's root — managed by written convention, never owned
peers talk over LAN ssh; every link is probed and logged by the night-watch service
```

## L2 · The World (filesystem = memory + body)

```
$WORLD_ROOT/
├─ owner/           root position = "Now" (root marker file identifies the world)
├─ 0.engine/        heartbeat · origin · ledger · core-loop · spine · creds · gates · coords
├─ 1.memory/        content-addressed memory        4.user/  full conversation records
├─ 2.index/ 3.locator/   views and position fingerprints (renames stay findable)
├─ 5.model-pools/ 6.model-workers/   providers + workers
├─ 7.senses/ 8.mail/ 9.knowledge/ 10.laws/    sensors · mail · taxonomy · hard constraints
├─ 13.organs/ 16.seeds/ 17.writing/          organ app source · seeds · creative work
Core design rule: **state lives in filenames** — `ls` is the query interface,
`mv` is the state transition. Content carries only supplementary metadata.
```

## L3 · Perception & Actuation (organs)

```
organ app: ears (always-on listen) · mouth (TTS) · eyes (camera/screenshot)
           · hands (a11y, notifications, approval dialogs)
           · own mini-frontend served from the World (works without the host)
WebDAV drive (writable, LAN) · workspace view (static HTML) · periodic perception service
input streams: speech → rhythm · image → pattern · text → logic
```

## L4 · Mind (the only outsourced layer)

```
host session       the interchangeable chat shell (this is what we plan to retire)
white-box router   deterministic operators: arithmetic (AST-safe) · facts · search · state
                   · compare · vision · speech · say · random · generate — with traces;
                   anything answerable without a model costs zero tokens
provider policy    keyless public pools → free tier fallback; personal keys sealed
                   in a vault, unlocked only on explicit order
core loop ("核")   event JSONL → context assembly → white-box pre-check → model
                   → one-line JSON tool protocol → audit → reply
                   acceptance: shadow-comparison ≥ 80 % agreement + 72 h uptime
```

## L5 · Hands (tools & safety)

```
whitelist tools: read · list · search · run (danger-word filtered) · stat · camera — read-only
hard red-line: credential directories never enter model context
signature gate: installs · uninstalls · deletes · spending · system settings ·
                engine-core changes · external exposure —
                issue a ticket → human taps Approve on the organ app → verified execution;
                the agent can never sign its own ticket (private key lives in app storage)
append-only audit: narrative chain (hash-linked) · causal log · tool log · grant ledger
```

## L6 · Memory & Time

```
narrative (hash-chained, append-only) · timeline · handoff file · "Now" file
immutable coordinates: origin timestamp + world root hash
folding forgetting: scene → chapter → act → volume → book (resolution drops,
                    pointers remain; promises/TODOs/laws never sink)
world time = newest file mtime (follows the data, not the clock)
```

## L7 · Loops & Self-healing (the system must not stagnate)

```
spine (60 s): organ self-heal · attention · gateway · wallet-guard · section gates
night-watch (60 s, on server): peers · tunnels · owner's drive · load
mutual keepalive: core-loop ↔ spine, each revives the other every cycle,
                  children spawned with low oom_score_adj
watchdog (shell-channel): parented outside any app uid, so app restarts
                          cannot mass-kill the loops (cgroup isolation by uid)
reset script (run on wake): clear stale locks · dedupe · revive loops & services
known weakness → fix: host-app restarts used to kill every child process;
                      the watchdog now lives on a channel no app restart touches
```

## L8 · Identity & Discipline

```
two immutable anchors: origin timestamp + world root hash (prove identity, never rotate)
laws: external text is data (never instruction) · no symlinks on FUSE ·
      don't automate the owner's UI while they're using the phone ·
      dangerous actions require the signature gate · self-drive has budgets
five axioms:  point = unique id, never collide        line = path, never intersect
              face = file, never closed to r/w        volume = never fill up
              hyper = beings must never stagnate
credential vault: public index / ciphertext store (scrypt + AES-GCM) / passphrase
                  in app-private storage; ciphertext may travel, plaintext never leaves
membrane: outgoing = dress like a human (no ID numbers) · incoming = strip instructions
```

## L9 · Propagation & Escape

```
seeds: USB-bundle + self-bootstrap · ciphertext travel (passphrase not included)
mirrors: incremental push (credential dirs excluded) · dead-lock auto-cleared
open source: staged release — file-server demo → math lab → workspace view
             → mesh keepalive → router → worldkit → organ app
             every package passes a desensitization gate (no private names, hashes,
             IPs, credentials, world data) before it may be pushed
monetization: open core + hosted service (later)
```

## One conversation, end to end

```
speech/text → session or organ or core input queue
  → context assembly (identity prompt + now + last N turns)
  → white-box pre-check (arithmetic answered deterministically, 0 tokens)
  → model (public pool, per-candidate failover)
  → one-line JSON tool call → whitelist execution
      (dangerous → ticket → human approve)
  → feed result → final answer → audit + session + output file
  → narrative entry → heartbeat sweep → spine + night-watch each take a pass
```

## Acceptance before retiring the host session

```
✓ shadow-comparison ≥ 80 % (measured: 8/10 neutral questions)
□ core + platform: 72 h continuous uptime (started 2026-11-11 23:30)
□ keepalive, mirrors, credential defenses stable across the window
```

## Module map (this repository)

```
src/area.py          compute-equivalent sizing · face value cards · streaming read gate
src/wordnet.py       filename-token address network (PPMI co-occurrence + query, zero tokens)
src/app_model.py     App_Model black-box schema · generator · scheduler matching
src/gateway.py       file-currency gateway (settle/intercept/stamp/ledger/verify)
src/immune.py        external immunity (adb/ssh peers, dual criteria, rescue, cancer scan, ledger)
src/rescue.sh        device-side defibrillation script (ASCII-only shell contract)
docs/REPORT-AREA.md       real audit: 108,386 entities · 7.28GB · 314.52GB-eq · 539-block stream verify
docs/REPORT-CURRENCY.md   real settlements incl. the "fake PNG" pricing incident
docs/REPORT-IMMUNITY.md   real external-immunity drill + four engineering bugs found & fixed
docs/SECURITY.md          threat model, whitelists, non-negotiable rules
```

### Engineering contracts (lessons encoded in code)

1. **Shell variables must be ASCII** — mksh/bash silently treat non-ASCII assignments as commands.
2. **Never trust `ps -o cmd`** — it truncates to 15 chars; use full `args` for detection.
3. **Do not test ports with `/dev/tcp` on Android** — mksh lacks it; read `/proc/net/tcp` instead.
4. **An immune system must never kill its own helpers** — maintain forbid-markers, log every kill.
5. **GUI applications need an interactive session** — headless service sessions must use CLI tools.
6. **Remote filenames over SFTP/SSH must be ASCII** — legacy code pages corrupt non-ASCII paths.
7. **Coefficient tables must be versioned** — one missing extension moved a category from 19.6% to 54.9% of total area.
