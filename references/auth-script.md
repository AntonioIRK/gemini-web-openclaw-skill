# Authentication script for agents and operators

Use this script when guiding a human through Gemini authentication for this skill.

## Core rule

Authentication happens on the same host where the persistent Gemini browser profile lives.

- local OpenClaw host -> local login
- remote OpenClaw host -> remote server-side login
- no usable GUI on the real host -> do not bluff a headless auth path

## What to tell the user before starting

Use wording close to this:

> The skill is installed. The next step is Gemini authentication.
> Authentication happens in the browser on the same host where OpenClaw runs and where the Gemini profile will be stored.
> If OpenClaw is local, login will be local.
> If OpenClaw is on a server, login will happen in the server-hosted browser session.

## Local-host script

Suggested wording:

> I am opening Gemini login in a fresh local browser profile for this skill.
> Please sign into Google and wait until Gemini home finishes loading.
> After that I will verify the profile and available Gemini surfaces.

Suggested steps:

```bash
./scripts/setup.sh
./scripts/gemini_web_login.sh
./scripts/gemini_web_doctor.sh
./scripts/gemini_web_inspect_home.sh
```

After successful login, say:

> Authentication is complete. I am now verifying that the Gemini profile is saved correctly and that Gemini home is available.

## Remote-host script

Before asking for login, say something like:

> Important: OpenClaw is running on a remote host, so Gemini login will happen in the browser session on that remote host.
> The Gemini profile will also stay on that remote host.
> Google may treat this as a new device or unusual location.
> If you do not want to log into Google on the remote host, local installation is the better option.

Then confirm:

- there is a usable GUI desktop session on the remote host
- the user or operator can actually reach it over RDP, VNC, xrdp, Tailscale, or another private desktop path

If there is no usable GUI, say:

> This host does not currently have a usable desktop path for Gemini login.
> I am not going to pretend a headless auth flow is reliable here.
> The correct next step is either adding remote desktop access or installing the skill locally instead.

If remote GUI exists, say:

> Please open the remote desktop session, complete Google and Gemini login there, and wait until Gemini home finishes loading. After that I will verify the saved profile.

Suggested steps:

```bash
./scripts/setup.sh
./scripts/gemini_web_login.sh
./scripts/gemini_web_doctor.sh
./scripts/gemini_web_inspect_home.sh
```

## If login fails

### If Google loops back to sign-in

Say:

> The login does not look stable yet. Either Google verification is incomplete or this host/profile is not trusted enough.
> I can retry once, but if it repeats, the better answer is local install or a more stable remote desktop host.

### If the host is headless

Say:

> This host does not have a practical GUI path for Gemini login.
> I recommend local install instead of forcing a brittle headless setup.

### If the user does not want Google login on the server

Say:

> That is a valid constraint. In that case, server-side Gemini auth is the wrong model here, and local install is the better path.

## After successful auth

Suggested verification order:

```bash
./scripts/gemini_web_doctor.sh
./scripts/gemini_web_inspect_home.sh
./scripts/gemini_web.sh chat-ask --prompt "Reply with exactly: OK"
```

Then optionally continue with:

```bash
./scripts/gemini_web_image_create.sh --prompt "A simple red kite on a blue sky"
./scripts/gemini_web_image_edit.sh --file ./test.jpg --prompt "Add a realistic UFO in the sky"
```

## Agent summary

If an agent remembers only one thing, it should be this:

> Authentication must happen where the persistent Gemini profile lives.
> No GUI means no honest auth path.
> When in doubt, recommend local install instead of pretending headless remote login is fine.
