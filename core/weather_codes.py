from dataclasses import dataclass
from enum import Enum, auto


class WeatherCondition(Enum):
    CLEAR = auto()
    PARTLY_CLOUDY = auto()
    OVERCAST = auto()
    FOG = auto()
    DRIZZLE = auto()
    FREEZING_RAIN = auto()
    RAIN = auto()
    SNOW = auto()
    SNOW_GRAINS = auto()
    RAIN_SHOWERS = auto()
    SNOW_SHOWERS = auto()
    THUNDERSTORM = auto()
    THUNDERSTORM_HAIL = auto()


CONDITION_CN: dict[WeatherCondition, str] = {
    WeatherCondition.CLEAR: "晴",
    WeatherCondition.PARTLY_CLOUDY: "多云",
    WeatherCondition.OVERCAST: "阴",
    WeatherCondition.FOG: "雾",
    WeatherCondition.DRIZZLE: "毛毛雨",
    WeatherCondition.FREEZING_RAIN: "冻雨",
    WeatherCondition.RAIN: "雨",
    WeatherCondition.SNOW: "雪",
    WeatherCondition.SNOW_GRAINS: "雪粒",
    WeatherCondition.RAIN_SHOWERS: "阵雨",
    WeatherCondition.SNOW_SHOWERS: "阵雪",
    WeatherCondition.THUNDERSTORM: "雷暴",
    WeatherCondition.THUNDERSTORM_HAIL: "雷暴冰雹",
}


def wind_direction_cn(degrees: int) -> str:
    """Convert wind direction in degrees to Chinese compass name."""
    dirs = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
    idx = round(degrees / 45) % 8
    return dirs[idx]


@dataclass
class Conditions:
    condition: WeatherCondition
    is_raining: bool
    is_snowing: bool
    is_thunderstorm: bool
    is_cloudy: bool
    is_foggy: bool
    rain_intensity: str  # "light" | "moderate" | "heavy"
    snow_intensity: str  # "light" | "medium" | "heavy"


WMO_MAP: dict[int, WeatherCondition] = {
    0: WeatherCondition.CLEAR,
    1: WeatherCondition.PARTLY_CLOUDY,
    2: WeatherCondition.PARTLY_CLOUDY,
    3: WeatherCondition.OVERCAST,
    45: WeatherCondition.FOG,
    48: WeatherCondition.FOG,
    51: WeatherCondition.DRIZZLE,
    53: WeatherCondition.DRIZZLE,
    55: WeatherCondition.DRIZZLE,
    56: WeatherCondition.FREEZING_RAIN,
    57: WeatherCondition.FREEZING_RAIN,
    61: WeatherCondition.RAIN,
    63: WeatherCondition.RAIN,
    65: WeatherCondition.RAIN,
    66: WeatherCondition.FREEZING_RAIN,
    67: WeatherCondition.FREEZING_RAIN,
    71: WeatherCondition.SNOW,
    73: WeatherCondition.SNOW,
    75: WeatherCondition.SNOW,
    77: WeatherCondition.SNOW_GRAINS,
    80: WeatherCondition.RAIN_SHOWERS,
    81: WeatherCondition.RAIN_SHOWERS,
    82: WeatherCondition.RAIN_SHOWERS,
    85: WeatherCondition.SNOW_SHOWERS,
    86: WeatherCondition.SNOW_SHOWERS,
    95: WeatherCondition.THUNDERSTORM,
    96: WeatherCondition.THUNDERSTORM_HAIL,
    99: WeatherCondition.THUNDERSTORM_HAIL,
}


def _rain_intensity(wmo: int) -> str:
    if wmo in (51, 56, 61, 66, 80):
        return "light"
    if wmo in (53, 63, 81):
        return "moderate"
    return "heavy"


def _snow_intensity(wmo: int) -> str:
    if wmo in (71, 85):
        return "light"
    if wmo in (73, 77, 86):
        return "medium"
    return "heavy"


def classify(wmo_code: int, is_day: bool) -> Conditions:
    condition = WMO_MAP.get(wmo_code, WeatherCondition.CLEAR)

    is_raining = condition in (
        WeatherCondition.DRIZZLE,
        WeatherCondition.FREEZING_RAIN,
        WeatherCondition.RAIN,
        WeatherCondition.RAIN_SHOWERS,
        WeatherCondition.THUNDERSTORM,
        WeatherCondition.THUNDERSTORM_HAIL,
    )
    is_snowing = condition in (
        WeatherCondition.SNOW,
        WeatherCondition.SNOW_GRAINS,
        WeatherCondition.SNOW_SHOWERS,
    )
    is_thunderstorm = condition in (
        WeatherCondition.THUNDERSTORM,
        WeatherCondition.THUNDERSTORM_HAIL,
    )
    is_cloudy = condition in (
        WeatherCondition.PARTLY_CLOUDY,
        WeatherCondition.OVERCAST,
    )
    is_foggy = condition == WeatherCondition.FOG

    return Conditions(
        condition=condition,
        is_raining=is_raining,
        is_snowing=is_snowing,
        is_thunderstorm=is_thunderstorm,
        is_cloudy=is_cloudy,
        is_foggy=is_foggy,
        rain_intensity=_rain_intensity(wmo_code) if is_raining else "light",
        snow_intensity=_snow_intensity(wmo_code) if is_snowing else "light",
    )
