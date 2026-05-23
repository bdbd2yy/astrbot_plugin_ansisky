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

<!-- Add issues encountered and solutions here as you go -->
