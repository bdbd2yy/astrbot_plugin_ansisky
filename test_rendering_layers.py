"""Fast assertions for sky layering and background colours."""

from core.animations import (
    AnimationController,
    CloudSystem,
    MoonSystem,
    SunSystem,
)
from core.scene import BACKGROUND_DAY, BACKGROUND_NIGHT, build_static_grid
from core.weather_codes import Conditions, WeatherCondition


def _clear_conditions() -> Conditions:
    return Conditions(
        condition=WeatherCondition.CLEAR,
        is_raining=False,
        is_snowing=False,
        is_thunderstorm=False,
        is_cloudy=False,
        is_foggy=False,
        rain_intensity="light",
        snow_intensity="light",
    )


def test_day_night_backgrounds_are_distinct_sky_colours() -> None:
    day_bg = build_static_grid(is_day=True)[0][0][1]
    night_bg = build_static_grid(is_day=False)[0][0][1]

    assert day_bg == BACKGROUND_DAY
    assert night_bg == BACKGROUND_NIGHT
    assert day_bg != night_bg
    assert sum(day_bg) > sum(night_bg)
    assert day_bg[2] > day_bg[0] and day_bg[2] > day_bg[1]
    assert max(night_bg) <= 40


def test_clouds_render_after_sun_and_moon() -> None:
    conditions = _clear_conditions()

    day = AnimationController()
    day.init_for_conditions(conditions, is_day=True, moon_phase=0.5)
    day_types = [type(system) for system in day.systems]
    assert day_types.index(SunSystem) < day_types.index(CloudSystem)

    night = AnimationController()
    night.init_for_conditions(conditions, is_day=False, moon_phase=0.5)
    night_types = [type(system) for system in night.systems]
    assert night_types.index(MoonSystem) < night_types.index(CloudSystem)


def test_cloud_silhouette_masks_existing_celestial_characters() -> None:
    conditions = _clear_conditions()
    cloud = CloudSystem(conditions)
    cloud._clouds = [{  # noqa: SLF001 - pin one cloud for render-layer regression
        "x": 10.0,
        "y": 5.0,
        "shape": 0,
        "speed": 0.0,
        "wind_x": 0.0,
    }]

    grid = build_static_grid(is_day=True)
    # This position is inside the second line of shape 0:
    # " .-(    ). " -- it is a cloud interior space, not leading/trailing
    # padding.  It must still erase a sun/moon glyph behind the cloud.
    interior_x = 10 + 4
    interior_y = 5 + 1
    grid[interior_y][interior_x] = ("S", (225, 210, 145))

    cloud.render(grid)

    assert grid[interior_y][interior_x] == (" ", BACKGROUND_DAY)


if __name__ == "__main__":
    test_day_night_backgrounds_are_distinct_sky_colours()
    test_clouds_render_after_sun_and_moon()
    test_cloud_silhouette_masks_existing_celestial_characters()
    print("rendering layer tests passed")
