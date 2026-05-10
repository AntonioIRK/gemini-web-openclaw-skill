# Docker setup for Gemini Web

This setup allows you to run the persistent Gemini browser profile inside a headless Docker container and interact with it through a browser (noVNC) for initial login.

## Quick Start

1. Start the container:
   ```bash
   docker compose up -d
   ```

2. Open the noVNC web interface in your browser:
   http://localhost:6080/vnc.html (Click "Connect", no password required)

3. Run the login script inside the container:
   ```bash
   docker compose exec gemini-web ./scripts/gemini_web_login.sh
   ```
   *You will see the browser open in your noVNC window. Complete the Google login manually.*

4. After logging in, close the browser in VNC or press `Ctrl+C` in the terminal. The session is now saved in `.gemini-web-profile`.

5. Test the installation:
   ```bash
   docker compose exec gemini-web ./scripts/gemini_web_doctor.sh
   docker compose exec gemini-web ./scripts/gemini_web_inspect_home.sh
   ```

## Using with OpenClaw

When running OpenClaw in a Docker environment, make sure to mount the `.gemini-web-profile` volume into the OpenClaw worker container, or just route requests directly into this container.
