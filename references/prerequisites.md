# Prerequisites

This repo is currently aimed at Linux hosts with Python 3.11+.

## Supported baseline

- Python 3.11 or newer
- Linux x86_64 with a working GUI browser path for real Gemini login
- Chromium or Google Chrome available locally, or installable by Playwright
- Enough disk space for a persistent browser profile and Playwright browser assets

## Best-tested host shape

- Ubuntu 24.04 or 22.04
- desktop or desktop-capable host
- Python 3.12 or 3.11
- network access to Gemini Web

## Python requirement

This package requires Python `>=3.11`.

Agents should stop immediately on Python 3.10 or older and ask the operator to upgrade Python first.

## Linux packages for GUI-capable hosts

On Ubuntu or Debian-like hosts, start with:

```bash
sudo apt-get update
sudo apt-get install -y \
  python3 python3-venv python3-pip \
  libnss3 libatk-bridge2.0-0 libgtk-3-0 libxkbcommon0 \
  libgbm1 libasound2t64 libxshmfence1 libxrandr2 libxdamage1 \
  libxfixes3 libxcomposite1 libx11-xcb1 libxcursor1 libxi6 \
  libxtst6 libglib2.0-0 libdrm2 ca-certificates fonts-liberation
```

If the host must support remote GUI login, also install a desktop stack such as XFCE plus xrdp or VNC. See `references/remote-install-and-auth.md`.

## What is not a good default target

- headless VPS with no usable GUI access
- Python 3.10 or older
- locked-down environments where browser profile persistence is impossible
- environments where the user will not accept Google login on the host that runs OpenClaw

## Required human expectations

- one-time Google login happens on the same host where the persistent Gemini profile lives
- Google may require 2FA or extra verification
- remote-server login is an operator workflow, not a magic end-user onboarding path
