import aiohttp
from pathlib import Path

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig

from .core.weather_api import fetch, WeatherData
from .core.weather_codes import classify, Conditions, CONDITION_CN, wind_direction_cn
from .core.scene import build_static_grid, ROWS, overlay_text
from .core.animations import AnimationController
from .core.renderer import render_frame
from .core.gif_composer import save_gif


@register("astrbot_plugin_ansisky", "bdbd2yy", "ASCII 艺术风格天气动画 GIF 插件", "1.0.0")
class AnsiSkyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context, config)
        self.config = config or {}
        self._session: aiohttp.ClientSession | None = None

    async def initialize(self):
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=15)
        )
        logger.info("AnsiSky plugin initialized")

    async def terminate(self):
        if self._session:
            await self._session.close()
        logger.info("AnsiSky plugin terminated")

    @filter.command("weather", alias={"天气", "tianqi"})
    async def weather(self, event: AstrMessageEvent):
        city = event.message_str.replace("/weather", "").replace("/天气", "").strip()
        if not city:
            city = self.config.get("default_city", "Beijing") if self.config else "Beijing"

        try:
            data: WeatherData = await fetch(self._session, city)
        except Exception as e:
            logger.error(f"Weather fetch failed for {city!r}: {e}")
            yield event.plain_result(f"获取天气失败: {e}")
            return

        conditions: Conditions = classify(data.wmo_code, data.is_day)

        grid = build_static_grid(data.is_day)

        anim_ctrl = AnimationController()
        anim_ctrl.init_for_conditions(conditions, data.is_day, data.moon_phase)

        frames = []
        frame_count = int(self.config.get("gif_frame_count", 12)) if self.config else 12
        frame_duration = int(self.config.get("gif_frame_duration_ms", 150)) if self.config else 150

        for _ in range(frame_count):
            anim_ctrl.step_frame(conditions)
            frame_grid = [row[:] for row in grid]
            anim_ctrl.render_all(frame_grid)
            overlay_text(
                frame_grid,
                f"{data.city}  {CONDITION_CN[conditions.condition]}  {data.temperature:.0f}°C  "
                f"{wind_direction_cn(data.wind_direction)}风{data.wind_speed:.1f}m/s",
                2, ROWS - 2, (255, 255, 255),
            )
            frame = render_frame(frame_grid)
            frames.append(frame)

        data_dir = Path(self.data_dir) if hasattr(self, "data_dir") else Path("/tmp/ansisky")
        data_dir.mkdir(parents=True, exist_ok=True)
        gif_path = data_dir / f"weather_{data.city}_{int(data.temperature)}.gif"
        save_gif(frames, gif_path, frame_duration)

        yield event.image_result(str(gif_path))
