# CLAUDE.md — astrbot_plugin_ansisky

## Project

AstrBot weather plugin that generates animated ASCII art weather GIFs using Open-Meteo API and Pillow.
- Optimize for boring, maintainable code: explicit is better than magical, replaceable is better than clever, and predictable is better than impressive

Plan: `/home/bdbd/.claude/plans/witty-launching-matsumoto.md`

## Rules

### Commits
- Commit after each completed file or logical unit (e.g., after `weather_codes.py` + `weather_api.py`, after `renderer.py` + `gif_composer.py`, etc.)
- Use conventional commit messages: `feat: add <file> — <short description>`
- Do NOT commit until the current file is complete and tested

### Code style
- Follow AstrBot plugin conventions; mirror existing plugins in `../` when unsure
- Keep handlers direct and the call hierarchy flat
- Write Unix-style Python: small, composable, explicit, and predictable
- Prefer simple control flow over clever abstractions or hidden magic
- Keep side effects visible: HTTP, filesystem, logging, and message sending should be obvious
- Use `aiohttp` for all HTTP calls; never use `requests`
- Use `from astrbot.api import logger`; never use Python `logging`
- Avoid overengineering: no unnecessary class trees, registries, decorators, or framework-like layers
- Use modern, readable Python: type hints, clear names, early returns, and minimal mutable global state
- Preserve existing command names and user-facing behavior unless explicitly required

### Testing
- After writing renderer + gif_composer: generate a test GIF with sample grid data
- After writing weather_api: fetch real data for Beijing and print it
- After full integration: send `/weather Beijing` in AstrBot and verify GIF output

## Development Log

### 2026-05-23 — Network and config fixes

**1. Nominatim blocked in China** — `nominatim.openstreetmap.org` is inaccessible from China. Replaced with Open-Meteo's free geocoding API (`geocoding-api.open-meteo.com/v1/search`). Same provider as the weather data, no API key required. Response field names differ: `lat`/`lon` → `latitude`/`longitude`, and results are wrapped in `{"results": [...]}` instead of a flat array.

**2. Open-Meteo 400 Bad Request** — `moon_phase` is not a valid `daily` parameter in Open-Meteo's forecast API. Requesting it causes HTTP 400. The API only supports `sunrise` and `sunset` as astronomical daily variables. Solution: compute moon phase locally from the date using a standard synodic month formula (29.530588 days).

**3. `self.config` not set by `Star.__init__`** — The AstrBot `Star` base class accepts a `config` parameter but does NOT store it as `self.config`. Each plugin must do this manually: `self.config = config or {}`. Always check sibling plugins for conventions before assuming base class behavior.

### 2026-05-23 — Visual style update (weathr-inspired)

Reworked scene.py to match the visual style of the [weathr](https://github.com/Veirt/weathr) terminal weather app:

- **Color palette**: Day sky changed to Cyan `(0,255,255)`, night sky to DarkBlue `(0,0,139)`. Roof now DarkRed by day, DarkMagenta by night. Windows Cyan by day, Yellow (lit) by night. Walls use tan/brown wood tones.
- **Ground**: Replaced random grass/soil generation with deterministic pseudo-random pattern — horizon row has grass (`^`, `,`) and flowers (`*`) in rotating colors; deeper rows use soil chars (`~`, `.`).
- **House**: Per-character coloring based on row position (roof/window/door/trim/wood) with day/night variants, matching weathr's `WorldSceneStyle`.
- **Decorations**: Added mailbox (left of tree), 2-row fence (right of house), pine tree art updated to match weathr's `*` chars. Tree trunk chars (`_`, `|`) get distinct trunk color.
- **Layout**: House at x=6, tree at x=0, mailbox at x=16, fence at x=68 — fits within the 80×30 grid.
