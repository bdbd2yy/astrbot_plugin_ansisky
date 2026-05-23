import datetime as dt
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

import aiohttp


@dataclass
class WeatherData:
    city: str
    lat: float
    lon: float
    wmo_code: int
    temperature: float
    humidity: int
    wind_speed: float
    wind_direction: int
    is_day: bool
    sunrise: Optional[str]
    sunset: Optional[str]
    moon_phase: float


def _compute_moon_phase() -> float:
    """Return moon phase 0.0–1.0 (0=new, 0.5=full) for today."""
    known_new = dt.date(2000, 1, 6)
    days = (dt.date.today() - known_new).days
    return (days % 29.530588) / 29.530588


async def _reverse_geocode(
    session: aiohttp.ClientSession, lat: float, lon: float
) -> str | None:
    """Try to get a place name for the given coordinates. Returns None on failure."""
    url = (
        f"https://nominatim.openstreetmap.org/reverse"
        f"?lat={lat}&lon={lon}&format=json&zoom=10"
    )
    try:
        async with session.get(
            url, headers={"User-Agent": "astrbot_plugin_ansisky/1.0"},
            timeout=aiohttp.ClientTimeout(total=5),
        ) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get("name") or data.get("display_name")
    except Exception:
        return None


async def fetch(
    session: aiohttp.ClientSession,
    city: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
) -> WeatherData:
    """Fetch weather by city name or coordinates via Open-Meteo APIs."""
    display_city: str

    if lat is not None and lon is not None:
        # Coordinates mode: skip forward geocoding, try reverse for display name
        reverse_name = await _reverse_geocode(session, lat, lon)
        display_city = reverse_name if reverse_name else f"{lat:.2f}, {lon:.2f}"
    else:
        # City mode: geocode city name → lat/lon
        encoded = quote(city)
        geo_url = (
            f"https://geocoding-api.open-meteo.com/v1/search"
            f"?name={encoded}&count=1&language=en&format=json"
        )
        async with session.get(geo_url) as resp:
            resp.raise_for_status()
            geo_data = await resp.json()

        geo_results = geo_data.get("results")
        if not geo_results:
            raise ValueError(f"City not found: {city!r}")

        lat = float(geo_results[0]["latitude"])
        lon = float(geo_results[0]["longitude"])
        display_city = city

    # Fetch weather from Open-Meteo
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=weather_code,temperature_2m,relative_humidity_2m,"
        f"wind_speed_10m,wind_direction_10m,is_day"
        f"&daily=sunrise,sunset"
        f"&timezone=auto"
    )
    async with session.get(weather_url) as resp:
        resp.raise_for_status()
        data = await resp.json()

    current = data["current"]
    daily = data.get("daily", {})

    return WeatherData(
        city=display_city,
        lat=lat,
        lon=lon,
        wmo_code=current["weather_code"],
        temperature=current["temperature_2m"],
        humidity=current["relative_humidity_2m"],
        wind_speed=current["wind_speed_10m"],
        wind_direction=current["wind_direction_10m"],
        is_day=bool(current.get("is_day", 1)),
        sunrise=daily.get("sunrise", [None])[0] if daily.get("sunrise") else None,
        sunset=daily.get("sunset", [None])[0] if daily.get("sunset") else None,
        moon_phase=_compute_moon_phase(),
    )
