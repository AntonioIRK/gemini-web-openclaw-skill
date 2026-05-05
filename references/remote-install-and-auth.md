# Remote install and authentication runbook

Use this guide when OpenClaw is installed on a remote host and the human user is not physically at that machine.

## Core reality

Gemini Web automation in this repo depends on a persistent browser profile that lives on the machine where the automation runs.

That means:

- if OpenClaw runs on a local desktop, the Gemini profile lives on that desktop
- if OpenClaw runs on a remote server, the Gemini profile lives on that server
- Google login must happen in the browser session attached to that same profile

This is the main reason remote auth feels harder than local auth.

## Supported deployment modes

### 1. Local desktop or laptop, recommended

Best overall UX.

- OpenClaw runs on the same machine the user can access directly
- the user logs into Gemini locally
- the persistent profile stays local
- easiest to explain, easiest to support

### 2. Remote server with an accessible desktop session, workable

This is the main remote pattern that can work reliably.

Requirements:

- the server can run Chromium or Chrome with a GUI session
- the operator or user can access that GUI remotely
- the login is completed inside that remote desktop session

Typical access methods:

- Tailscale + RDP or VNC
- SSH with X11 forwarding, only for advanced operators and only when browser UX remains usable
- a remote desktop stack such as xrdp on Ubuntu
- a cloud VM or home server with a desktop environment plus Tailscale, WireGuard, or another trusted tunnel

CDP attach is not the normal auth path. Use it only if you explicitly intend to attach to an existing browser session and have set `GEMINI_WEB_ALLOW_CDP_ATTACH=1`.

### 3. Headless VPS with no practical GUI access, not recommended

This is the bad fit.

If the server is just a headless VPS with no usable desktop session:

- human login is awkward or impossible
- Google account verification is more likely to fail or become painful
- browser auth recovery becomes fragile

In this mode, a local install is usually the better answer.

## Supported concrete remote path, Ubuntu + XFCE + xrdp + Tailscale

If you need one specific remote recipe to hand to an agent, use this one.

### Host assumptions

- Ubuntu 22.04 or 24.04
- a real user account on the server, not just root shell access
- OpenClaw installed and running on that server
- Tailscale available on both the server and the operator or user machine

### Server preparation

```bash
sudo apt-get update
sudo apt-get install -y \
  xfce4 xfce4-goodies xrdp chromium-browser \
  python3 python3-venv python3-pip \
  libnss3 libatk-bridge2.0-0 libgtk-3-0 libxkbcommon0 \
  libgbm1 libasound2t64 libxshmfence1 libxrandr2 libxdamage1 \
  libxfixes3 libxcomposite1 libx11-xcb1 libxcursor1 libxi6 \
  libxtst6 libglib2.0-0 libdrm2 ca-certificates fonts-liberation
sudo systemctl enable --now xrdp
```

Install and connect Tailscale on the server in the operator's normal way, then confirm the server has a Tailscale IP.

### Remote desktop connection

From the local machine:

- connect to the server over Tailscale
- open an RDP client to the server's Tailscale IP
- log into the server's desktop session

At this point the operator should be looking at the server desktop, not just an SSH terminal.

Quick sanity checks inside the server session:

```bash
echo "$DISPLAY"
chromium-browser --version
```

Expected:

- `DISPLAY` is non-empty inside the desktop session
- Chromium starts normally from the server desktop

### Skill installation on the server

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/AntonioIRK/gemini-web-openclaw-skill.git gemini-web
cd gemini-web
./scripts/setup.sh
```

### Server-side Gemini login

Inside the same server desktop session:

```bash
cd ~/.openclaw/workspace/skills/gemini-web
./scripts/gemini_web_login.sh
```

Then:

- the browser opens on the server
- complete Google sign-in there
- complete any 2FA or confirmation prompts there
- wait until Gemini home finishes loading

### Validation after login

```bash
./scripts/gemini_web_doctor.sh
./scripts/gemini_web_inspect_home.sh
./scripts/gemini_web.sh chat-ask --prompt "Reply with exactly: OK"
```

Only after those succeed should agents rely on Gemini automation.

Expected result pattern:

- `doctor` returns JSON and `logged_in_guess` is `true`
- `inspect-home` returns JSON with a real Gemini page title and visible suggestions
- `chat-ask` returns structured JSON with `status: success` and a short text response

## Stop conditions, recommend local install instead

Agents should stop and recommend local installation if any of these are true:

- the server has no usable GUI session
- the operator cannot access a remote desktop session on the server
- the user does not want to sign into Google on the remote host
- Google repeatedly rejects or re-challenges the remote login environment
- the host is just a minimal headless VPS and nobody wants to maintain a GUI stack there

## Concrete remote desktop options

### Option A, xrdp

Good when the server has a Linux desktop environment.

Typical outline:

- install XFCE or another lightweight desktop
- install `xrdp`
- connect using an RDP client from the local machine
- start the login flow inside that remote desktop session

What agents should explain:

- the Google login is happening inside the remote server's browser
- the saved Gemini profile remains on the server
- future automation will reuse that server-side profile

### Option B, VNC

Good when VNC is already part of the operator environment.

Typical outline:

- install a desktop environment
- install a VNC server such as TigerVNC
- connect through a private tunnel such as Tailscale
- launch the browser and complete sign-in remotely

What agents should watch for:

- poor rendering performance
- clipboard issues during login
- users forgetting they are signing into the remote browser, not their local browser

### Option C, Tailscale + browser-capable node

Good when the operator already has Tailscale everywhere.

Pattern:

- put OpenClaw on a desktop-like machine reachable over Tailscale
- remote into that machine over RDP, VNC, or another GUI method
- complete login there

This is often better than using a minimal VPS.

## What agents should say before remote auth

Before asking a user to sign into Gemini on a remote host, explain clearly:

- the login will happen inside the remote server's browser profile
- the saved Gemini session will live on that server
- Google may treat this as a new device or unusual location
- the user may be asked for 2FA or additional confirmation
- if they are not comfortable with that, local installation is the better option

## Minimal remote-install checklist for agents

1. Confirm whether the host is local or remote.
2. If remote, confirm whether it has a usable GUI desktop session.
3. If there is no usable GUI, recommend local install instead of forcing a brittle server login path.
4. If there is a GUI, explain that Gemini auth will be server-side.
5. Ensure the repo is installed at `~/.openclaw/workspace/skills/gemini-web`.
6. Run `./scripts/setup.sh`.
7. Open a remote desktop session.
8. Run `./scripts/gemini_web_login.sh`.
9. Wait for Google login and any verification to complete.
10. Run `./scripts/gemini_web_doctor.sh`.
11. Run `./scripts/gemini_web_inspect_home.sh`.
12. Only then use `chat-ask`, `image-create`, or `image-edit`.

## Troubleshooting decisions for agents

### The server has no display

Stop and say so clearly.

Recommendation:

- either add a proper remote desktop stack
- or move the install to a local machine

Do not pretend headless auth is a good default.

### Google keeps returning to the sign-in screen

Possible causes:

- incomplete verification
- browser session not persisted correctly
- remote environment not trusted by Google

Agent response:

- retry the login flow once
- verify the same remote profile directory is being reused
- if the problem persists, recommend local install or a more stable remote desktop host

### The profile seems poisoned or expired

Signals:

- repeated redirects to Google auth
- Gemini home never loads even after successful sign-in

Agent response:

- explain that the persistent server-side profile may need to be reset
- back up or remove the profile directory only with operator approval
- then repeat setup and login

### The account does not show Storybook

That is not necessarily an installation failure.

Agent response:

- run `inspect-home`
- confirm what surfaces the account really exposes
- continue using reliable chat and image flows if those are available

## Honest recommendation

If the user is remote and wants the smoothest setup, prefer a local desktop install whenever possible.

Use server-side installation when:

- the operator understands remote desktop access
- the user accepts server-side Google login
- the host can keep a stable persistent GUI browser profile
