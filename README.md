# AnsiSky Weather

AnsiSky is an AstrBot plugin that generates animated ASCII-style weather GIFs.
It fetches current weather from Open-Meteo, renders a terminal-like landscape
with Pillow, and sends the generated GIF back to the chat.

The visual style is based on the `weathr` terminal weather app, including
line-art sun, cratered moon, drifting clouds, a small house scene, and dynamic
chimney smoke.

## Features

- Current weather by city name or latitude/longitude.
- Animated ASCII GIF output.
- Day and night palettes, with brighter daytime and darker nighttime scenes.
- Weather effects for rain, snow, thunderstorm, fog, clouds, stars, birds, sun,
  moon, and chimney smoke.
- Open-Meteo weather and geocoding APIs, no API key required.
- Configurable default city, frame count, and frame duration.

## Commands

```text
/weather
/weather Shanghai
/weather -c New York
/weather -l 39.90 116.40
```

Aliases:

```text
/天气 Beijing
/tianqi -l 31.23 121.47
```

Arguments:

- `-c <city>`: query by city name.
- `-l <lat> <lon>`: query by coordinates.
- No flag: treated as a city name for backward compatibility.
- Empty command: uses the configured `default_city`.

## Configuration

The plugin reads `_conf_schema.json` through AstrBot:

- `default_city`: fallback city when no command argument is provided.
- `gif_frame_count`: number of animation frames.
- `gif_frame_duration_ms`: duration of each GIF frame in milliseconds.

## Development

Install dependencies in the AstrBot environment:

```bash
pip install -r requirements.txt
```

Generate sample GIFs for all supported weather conditions:

```bash
python3 test_all_conditions.py /tmp/ansisky_samples
```

The sample generator writes day and night GIFs to the output directory, which is
useful for visual regression checks after changing scene or animation code.

## Project Layout

```text
main.py                 AstrBot command handler
core/weather_api.py     Open-Meteo geocoding and forecast client
core/weather_codes.py   WMO weather code classification
core/scene.py           Static ASCII scene and day/night palettes
core/animations.py      Animated weather and world effects
core/renderer.py        Character grid to Pillow image renderer
core/gif_composer.py    GIF composition helpers
test_all_conditions.py  Local visual sample generator
```

## Notes

- The reference images `sun.png`, `moon.png`, and `house.png` document the
  target visual style for the corresponding ASCII scene elements.
- Generated GIF files are written to the plugin data directory when available,
  or `/tmp/ansisky` as a fallback.
