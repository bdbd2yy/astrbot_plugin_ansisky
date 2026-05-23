"""Generate sample weather GIFs for all conditions.

Usage:  python3 test_all_conditions.py [output_dir]
        (defaults to /tmp/ansisky_samples)
"""

import sys
from pathlib import Path

from core.scene import build_static_grid, ROWS, overlay_text
from core.animations import AnimationController
from core.weather_codes import (
    Conditions, WeatherCondition, CONDITION_EN,
)
from core.renderer import render_frame
from core.gif_composer import save_gif


def generate(
    cond: WeatherCondition,
    city: str,
    temp: float,
    wind_speed: float,
    is_day: bool,
    moon_phase: float,
    is_raining: bool,
    is_snowing: bool,
    is_thunderstorm: bool,
    is_cloudy: bool,
    is_foggy: bool,
    rain_intensity: str,
    snow_intensity: str,
    out_path: Path,
) -> None:
    grid = build_static_grid(is_day=is_day)
    conditions = Conditions(
        condition=cond,
        is_raining=is_raining,
        is_snowing=is_snowing,
        is_thunderstorm=is_thunderstorm,
        is_cloudy=is_cloudy,
        is_foggy=is_foggy,
        rain_intensity=rain_intensity,
        snow_intensity=snow_intensity,
    )
    anim = AnimationController()
    anim.init_for_conditions(conditions, is_day=is_day, moon_phase=moon_phase)
    frames = []
    for _ in range(12):
        anim.step_frame(conditions)
        fg = [row[:] for row in grid]
        anim.render_all(fg)
        hud = (
            f"City: {city} | Location: 39.90, 116.40 | Weather: {CONDITION_EN[cond]} | "
            f"Temp: {temp:.0f}°C | Wind: {wind_speed:.1f}km/h"
        )
        overlay_text(fg, hud, 2, ROWS - 2, (255, 255, 255))
        frames.append(render_frame(fg))
    save_gif(frames, out_path, 150)
    print(f"  {out_path.name}")


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/ansisky_samples")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Generating day-time scenes...")
    generate(WeatherCondition.CLEAR, "Beijing", 28, 12.6, True, 0.5,
             False, False, False, False, False, "light", "light",
             out_dir / "day_clear.gif")
    generate(WeatherCondition.PARTLY_CLOUDY, "Shanghai", 26, 15.1, True, 0.5,
             False, False, False, True, False, "light", "light",
             out_dir / "day_partly_cloudy.gif")
    generate(WeatherCondition.OVERCAST, "Guangzhou", 24, 18.0, True, 0.5,
             False, False, False, True, False, "light", "light",
             out_dir / "day_overcast.gif")
    generate(WeatherCondition.FOG, "Chengdu", 20, 5.4, True, 0.5,
             False, False, False, False, True, "light", "light",
             out_dir / "day_fog.gif")
    generate(WeatherCondition.DRIZZLE, "Hangzhou", 22, 10.8, True, 0.5,
             True, False, False, False, False, "light", "light",
             out_dir / "day_drizzle.gif")
    generate(WeatherCondition.RAIN, "Nanjing", 21, 23.4, True, 0.5,
             True, False, False, False, False, "moderate", "light",
             out_dir / "day_rain.gif")
    generate(WeatherCondition.RAIN_SHOWERS, "Wuhan", 23, 28.1, True, 0.5,
             True, False, False, False, False, "heavy", "light",
             out_dir / "day_rain_showers.gif")
    generate(WeatherCondition.SNOW, "Harbin", -5, 14.4, True, 0.5,
             False, True, False, False, False, "light", "medium",
             out_dir / "day_snow.gif")
    generate(WeatherCondition.SNOW_SHOWERS, "Changchun", -8, 19.8, True, 0.5,
             False, True, False, False, False, "light", "heavy",
             out_dir / "day_snow_showers.gif")
    generate(WeatherCondition.THUNDERSTORM, "Shenzhen", 27, 33.1, True, 0.5,
             True, False, True, False, False, "heavy", "light",
             out_dir / "day_thunderstorm.gif")

    print("Generating night-time scenes...")
    generate(WeatherCondition.CLEAR, "Beijing", 15, 7.2, False, 0.3,
             False, False, False, False, False, "light", "light",
             out_dir / "night_clear.gif")
    generate(WeatherCondition.PARTLY_CLOUDY, "Shanghai", 14, 12.6, False, 0.7,
             False, False, False, True, False, "light", "light",
             out_dir / "night_partly_cloudy.gif")
    generate(WeatherCondition.RAIN, "Nanjing", 12, 18.0, False, 0.5,
             True, False, False, False, False, "moderate", "light",
             out_dir / "night_rain.gif")
    generate(WeatherCondition.SNOW, "Harbin", -12, 12.6, False, 0.5,
             False, True, False, False, False, "light", "heavy",
             out_dir / "night_snow.gif")
    generate(WeatherCondition.THUNDERSTORM, "Shenzhen", 18, 30.6, False, 0.5,
             True, False, True, False, False, "heavy", "light",
             out_dir / "night_thunderstorm.gif")
    generate(WeatherCondition.FOG, "Chengdu", 10, 3.6, False, 0.5,
             False, False, False, False, True, "light", "light",
             out_dir / "night_fog.gif")

    print(f"\nDone! {len(list(out_dir.glob('*.gif')))} GIFs saved to {out_dir}/")


if __name__ == "__main__":
    main()
