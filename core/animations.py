"""Animation systems for ANSI Sky weather plugin.

Provides 10 particle/effect systems and an AnimationController that orchestrates
them based on weather conditions, time of day, and moon phase.

Grid convention: cells are (char, (r,g,b)) tuples accessed as grid[y][x].
Dimensions: 80 columns x 30 rows. Ground level is at row 24.
"""

from __future__ import annotations

import random
from typing import Optional

from .weather_codes import Conditions, WeatherCondition

# ---- grid dimensions ----
COLS: int = 100
ROWS: int = 36
Y_GROUND: int = 28

# ---- colour palette ----
STAR_COLOR: tuple[int, int, int] = (255, 255, 200)
MOON_COLOR: tuple[int, int, int] = (255, 255, 180)
SUN_COLOR: tuple[int, int, int] = (255, 200, 50)
CLOUD_COLOR: tuple[int, int, int] = (200, 200, 210)
BIRD_COLOR: tuple[int, int, int] = (80, 80, 80)
RAIN_COLOR: tuple[int, int, int] = (173, 216, 230)
SNOW_COLOR: tuple[int, int, int] = (255, 250, 250)
LIGHTNING_COLOR: tuple[int, int, int] = (255, 255, 100)
FOG_COLOR: tuple[int, int, int] = (200, 200, 200)
SMOKE_COLOR: tuple[int, int, int] = (180, 180, 180)

# ---- reusable shape data ----

CLOUD_SHAPES: list[list[str]] = [
    ["   __   __   ", " _(  )_(  )_ "],
    ["  ___  ___  ", " (   )(   ) "],
    ["   _____   ", " _(     )_ "],
    ["  __  __  ", " (  )(  ) "],
]

# Moon phase strings: phase 0.0 = new moon "(   )", 0.5 = full moon "()"
MOON_PHASE_STRINGS: list[str] = [
    "(   )",  # 0.000 - 0.125
    "(  )",   # 0.125 - 0.250
    "( )",    # 0.250 - 0.375
    "()",     # 0.375 - 0.500
    "()",     # 0.500 - 0.625
    "( )",    # 0.625 - 0.750
    "(  )",   # 0.750 - 0.875
    "(   )",  # 0.875 - 1.000
]

RAIN_CHARS: list[str] = ["|", "\\", "/"]
SNOW_CHARS: list[str] = ["*", "."]
BIRD_CHARS: list[str] = ["v", "^"]
SMOKE_CHARS: list[str] = ["@", "O", "o", "."]

# ---- base class ----


class AnimationSystem:
    """Duck-typing base for every effect system.

    Each subclass implements:
        is_active(conditions: Conditions) -> bool
        step() -> None
        render(grid) -> None
    """

    def is_active(self, conditions: Conditions) -> bool:  # noqa: ARG002
        return True

    def step(self) -> None:
        pass

    def render(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:  # noqa: ARG002
        pass


# ---- helper ----

def _in_bounds(x: int, y: int) -> bool:
    return 0 <= x < COLS and 0 <= y < ROWS


# ================================================================
# 1. StarSystem
# ================================================================


class StarSystem(AnimationSystem):
    """80 twinkling stars in the upper sky (rows 1-20).

    Always active; the controller adds it only at night.
    """

    def __init__(self) -> None:
        self._stars: list[dict] = []
        for _ in range(80):
            self._stars.append({
                "x": random.randint(0, COLS - 1),
                "y": random.randint(1, 20),
                "bright": random.choice([True, False]),
            })

    def step(self) -> None:
        # twinkle ~10 % of stars each frame
        n_twinkle = max(1, len(self._stars) // 10)
        for _ in range(n_twinkle):
            star = random.choice(self._stars)
            star["bright"] = not star["bright"]

    def render(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:
        for star in self._stars:
            x, y = star["x"], star["y"]
            if _in_bounds(x, y):
                ch = "*" if star["bright"] else "."
                grid[y][x] = (ch, STAR_COLOR)


# ================================================================
# 2. MoonSystem
# ================================================================


class MoonSystem(AnimationSystem):
    """Moon at (65, 3) with 8 ASCII phase variants.

    Always active; the controller adds it only at night.
    """

    MOON_X: int = 82
    MOON_Y: int = 3

    def __init__(self, moon_phase: float = 0.5) -> None:
        self.moon_phase: float = moon_phase

    def step(self) -> None:
        pass  # position fixed

    def _phase_string(self) -> str:
        idx = min(int(self.moon_phase * 8), 7)
        return MOON_PHASE_STRINGS[idx]

    def render(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:
        phase_str = self._phase_string()
        y = self.MOON_Y
        for i, ch in enumerate(phase_str):
            x = self.MOON_X + i
            if _in_bounds(x, y):
                grid[y][x] = (ch, MOON_COLOR)


# ================================================================
# 3. SunSystem
# ================================================================


class SunSystem(AnimationSystem):
    """Animated sun at (65, 2-3) with alternating ray frames.

    Always active; the controller adds it only during the day.
    """

    SUN_X: int = 82

    # Frame 0 rays (centre at y=3, top row y=2, bottom y=4)
    _FRAME_0: list[tuple[int, int, str]] = [
        (81, 2, "\\"), (82, 2, "|"), (83, 2, "/"),
        (81, 3, "-"), (82, 3, "O"), (83, 3, "-"),
        (81, 4, "/"), (82, 4, "|"), (83, 4, "\\"),
    ]

    # Frame 1 rays — mirrored diagonals
    _FRAME_1: list[tuple[int, int, str]] = [
        (81, 1, "/"), (82, 1, "|"), (83, 1, "\\"),
        (81, 2, "-"), (82, 2, "O"), (83, 2, "-"),
        (81, 3, "\\"), (82, 3, "|"), (83, 3, "/"),
    ]

    def __init__(self) -> None:
        self._frame: int = 0

    def step(self) -> None:
        self._frame = (self._frame + 1) % 2

    def render(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:
        cells = self._FRAME_1 if self._frame else self._FRAME_0
        for x, y, ch in cells:
            if _in_bounds(x, y):
                grid[y][x] = (ch, SUN_COLOR)


# ================================================================
# 4. CloudSystem
# ================================================================


class CloudSystem(AnimationSystem):
    """Drifting multi-line clouds.

    Cloud count adapts to conditions: 3 clear, 4 partly-cloudy, 5 otherwise.
    """

    def __init__(self, conditions: Conditions) -> None:
        if conditions.condition == WeatherCondition.CLEAR:
            n_clouds = 3
        elif conditions.condition == WeatherCondition.PARTLY_CLOUDY:
            n_clouds = 4
        else:
            n_clouds = 5

        self._clouds: list[dict] = []
        for _ in range(n_clouds):
            self._clouds.append({
                "x": float(random.randint(0, COLS - 1)),
                "y": random.randint(3, 16),
                "shape": random.randint(0, len(CLOUD_SHAPES) - 1),
                "speed": 1.0,
            })

    def step(self) -> None:
        for cloud in self._clouds:
            cloud["x"] -= cloud["speed"]
            if cloud["x"] < -15:
                cloud["x"] = float(COLS)
                cloud["y"] = random.randint(3, 16)
                cloud["shape"] = random.randint(0, len(CLOUD_SHAPES) - 1)

    def render(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:
        for cloud in self._clouds:
            shape = CLOUD_SHAPES[cloud["shape"]]
            cx = int(cloud["x"])
            cy = cloud["y"]
            for row_offset, line in enumerate(shape):
                for col_offset, ch in enumerate(line):
                    x = cx + col_offset
                    y = cy + row_offset
                    if _in_bounds(x, y) and ch != " ":
                        grid[y][x] = (ch, CLOUD_COLOR)


# ================================================================
# 5. BirdSystem
# ================================================================


class BirdSystem(AnimationSystem):
    """2-3 ASCII birds drifting right, flapping wings.

    Active only when it is not raining, snowing, or storming.
    """

    def __init__(self) -> None:
        n_birds = random.randint(2, 3)
        self._birds: list[dict] = []
        for _ in range(n_birds):
            self._birds.append({
                "x": float(random.randint(0, COLS - 1)),
                "y": random.randint(5, 22),
                "frame": random.randint(0, 1),
            })

    def is_active(self, conditions: Conditions) -> bool:
        return (
            not conditions.is_raining
            and not conditions.is_snowing
            and not conditions.is_thunderstorm
        )

    def step(self) -> None:
        for bird in self._birds:
            bird["x"] += 2.0
            bird["frame"] = 1 - bird["frame"]
            if bird["x"] >= COLS:
                bird["x"] = -3.0
                bird["y"] = random.randint(4, 12)

    def render(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:
        for bird in self._birds:
            x = int(bird["x"])
            y = bird["y"]
            ch = BIRD_CHARS[bird["frame"]]
            if _in_bounds(x, y):
                grid[y][x] = (ch, BIRD_COLOR)


# ================================================================
# 6. RainSystem
# ================================================================


class RainSystem(AnimationSystem):
    """Falling rain streaks at varying intensity.

    Particle count: light=20, moderate=40, heavy=60.
    """

    def __init__(self, intensity: str) -> None:
        intensity_counts = {"light": 30, "moderate": 60, "heavy": 90}
        self._target: int = intensity_counts.get(intensity, 20)
        self._particles: list[dict] = []

        # pre-fill initial particles spread across the fall column
        for _ in range(self._target):
            self._particles.append({
                "x": random.randint(0, COLS - 1),
                "y": float(random.randint(0, Y_GROUND - 1)),
                "char": random.choice(RAIN_CHARS),
            })

    def is_active(self, conditions: Conditions) -> bool:
        return conditions.is_raining

    def step(self) -> None:
        # move existing particles down
        for p in self._particles:
            p["y"] += 2.0

        # cull particles that have hit the ground
        self._particles = [p for p in self._particles if p["y"] < Y_GROUND]

        # spawn new particles to maintain visual density
        spawn_count = max(1, self._target // 8)
        for _ in range(spawn_count):
            if len(self._particles) < self._target + 10:
                self._particles.append({
                    "x": random.randint(0, COLS - 1),
                    "y": 0.0,
                    "char": random.choice(RAIN_CHARS),
                })

    def render(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:
        for p in self._particles:
            x = p["x"]
            y = int(p["y"])
            if _in_bounds(x, y):
                grid[y][x] = (p["char"], RAIN_COLOR)


# ================================================================
# 7. SnowSystem
# ================================================================


class SnowSystem(AnimationSystem):
    """Falling snowflakes with gentle horizontal sway.

    Particle count: light=20, medium=30, heavy=50.
    """

    def __init__(self, intensity: str) -> None:
        intensity_counts = {"light": 30, "medium": 45, "heavy": 75}
        self._target: int = intensity_counts.get(intensity, 20)
        self._particles: list[dict] = []

        for _ in range(self._target):
            self._particles.append({
                "x": float(random.randint(0, COLS - 1)),
                "y": float(random.randint(0, Y_GROUND - 1)),
                "char": random.choice(SNOW_CHARS),
            })

    def is_active(self, conditions: Conditions) -> bool:
        return conditions.is_snowing

    def step(self) -> None:
        for p in self._particles:
            p["y"] += 1.0
            p["x"] += random.choice([-1, 0, 1])

        self._particles = [p for p in self._particles if p["y"] < Y_GROUND]

        spawn_count = max(1, self._target // 8)
        for _ in range(spawn_count):
            if len(self._particles) < self._target + 10:
                self._particles.append({
                    "x": float(random.randint(0, COLS - 1)),
                    "y": 0.0,
                    "char": random.choice(SNOW_CHARS),
                })

    def render(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:
        for p in self._particles:
            x = int(p["x"])
            y = int(p["y"])
            if _in_bounds(x, y):
                grid[y][x] = (p["char"], SNOW_COLOR)


# ================================================================
# 8. ThunderstormSystem
# ================================================================


class ThunderstormSystem(AnimationSystem):
    """Lightning bolts that flash periodically.

    Generates 1-3 jagged bolts every 5-12 frames.
    Each flash persists for 2 frames.
    """

    def __init__(self) -> None:
        self._timer: int = random.randint(5, 12)
        self._flash_remaining: int = 0
        self._bolts: list[list[tuple[int, int, str]]] = []

    def is_active(self, conditions: Conditions) -> bool:
        return conditions.is_thunderstorm

    def step(self) -> None:
        if self._flash_remaining > 0:
            self._flash_remaining -= 1
            return

        self._timer -= 1
        if self._timer <= 0:
            self._trigger_lightning()
            self._timer = random.randint(5, 12)

    def _trigger_lightning(self) -> None:
        self._flash_remaining = 2
        self._bolts = []
        n_bolts = random.randint(1, 3)
        for _ in range(n_bolts):
            self._bolts.append(self._generate_bolt())

    def _generate_bolt(self) -> list[tuple[int, int, str]]:
        segments: list[tuple[int, int, str]] = []
        x: float = float(random.randint(25, 75))
        y: float = 0.0

        while y < Y_GROUND:
            dy = random.choice([1, 2])
            dx = random.choice([-1, 0, 1])
            y += dy
            x += dx
            if x < 0 or x >= COLS:
                break
            if dx == 0:
                ch = "|"
            elif dx < 0:
                ch = "/"
            else:
                ch = "\\"
            segments.append((int(x), int(y), ch))

        # add bright spark chars near the bolt for flash effect
        sparks: list[tuple[int, int, str]] = []
        for sx, sy, _ in segments[:8]:  # first 8 segments only
            for _ in range(2):
                ox = random.randint(-2, 2)
                oy = random.randint(-1, 1)
                sparks.append((sx + ox, sy + oy, "*"))

        return segments + sparks

    def render(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:
        if self._flash_remaining <= 0:
            return
        for bolt in self._bolts:
            for x, y, ch in bolt:
                if _in_bounds(x, y):
                    grid[y][x] = (ch, LIGHTNING_COLOR)


# ================================================================
# 9. FogSystem
# ================================================================


class FogSystem(AnimationSystem):
    """Slowly drifting fog wisps (`~` clusters).

    Active only when conditions indicate fog.
    """

    def __init__(self) -> None:
        n_wisps = random.randint(6, 10)
        self._wisps: list[dict] = []
        for _ in range(n_wisps):
            self._wisps.append({
                "x": float(random.randint(0, COLS - 1)),
                "y": random.randint(8, 22),
                "width": random.randint(3, 5),
            })

    def is_active(self, conditions: Conditions) -> bool:
        return conditions.is_foggy

    def step(self) -> None:
        for wisp in self._wisps:
            wisp["x"] -= 0.5
            if wisp["x"] < -6:
                wisp["x"] = float(COLS)
                wisp["y"] = random.randint(6, 20)

    def render(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:
        for wisp in self._wisps:
            wx = int(wisp["x"])
            wy = wisp["y"]
            for i in range(wisp["width"]):
                x = wx + i
                y = wy
                if _in_bounds(x, y):
                    grid[y][x] = ("~", FOG_COLOR)


# ================================================================
# 10. ChimneySmoke
# ================================================================


class ChimneySmoke(AnimationSystem):
    """Rising smoke from the house chimney.

    Particles rise and drift right, fading through @ -> O -> o -> . -> gone.
    Chimney source is at (58, 12).

    Active only when it is not raining or storming.
    """

    CHIMNEY_X: int = 48
    CHIMNEY_Y: int = 16
    MAX_PARTICLES: int = 15

    def __init__(self) -> None:
        self._particles: list[dict] = []

    def is_active(self, conditions: Conditions) -> bool:
        return not conditions.is_raining and not conditions.is_thunderstorm

    def step(self) -> None:
        # move existing particles up and right; age them
        for p in self._particles:
            p["y"] -= 0.5
            p["x"] += 0.3
            p["age"] += 1

        # cull old or out-of-bounds particles
        self._particles = [
            p for p in self._particles
            if p["age"] < len(SMOKE_CHARS)
            and p["y"] >= 0
            and p["x"] < COLS
        ]

        # spawn 1-2 new particles per frame
        spawn = random.randint(1, 2)
        for _ in range(spawn):
            if len(self._particles) < self.MAX_PARTICLES:
                self._particles.append({
                    "x": float(self.CHIMNEY_X),
                    "y": float(self.CHIMNEY_Y),
                    "age": 0,
                })

    def render(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:
        for p in self._particles:
            x = int(p["x"])
            y = int(p["y"])
            ch = SMOKE_CHARS[min(p["age"], len(SMOKE_CHARS) - 1)]
            if _in_bounds(x, y):
                grid[y][x] = (ch, SMOKE_COLOR)


# ================================================================
# AnimationController
# ================================================================


class AnimationController:
    """Owns and orchestrates all AnimationSystem instances.

    Usage::

        ctrl = AnimationController()
        ctrl.init_for_conditions(conditions, is_day=True, moon_phase=0.3)

        # each frame:
        ctrl.step_frame(conditions)       # advance all active systems
        ctrl.render_all(grid)             # draw onto the character grid
    """

    def __init__(self) -> None:
        self.systems: list[AnimationSystem] = []
        self._is_day: bool = True
        self._moon_phase: float = 0.5
        self._conditions: Optional[Conditions] = None

    # ------------------------------------------------------------------
    # setup
    # ------------------------------------------------------------------

    def init_for_conditions(
        self,
        conditions: Conditions,
        is_day: bool = True,
        moon_phase: float = 0.5,
    ) -> None:
        """Create and configure every relevant system for *conditions*."""
        self._is_day = is_day
        self._moon_phase = moon_phase
        self._conditions = conditions
        self.systems = []

        # ---- always present ----
        self.systems.append(CloudSystem(conditions))

        # ---- day / night exclusives ----
        if is_day:
            self.systems.append(SunSystem())
            if (
                not conditions.is_raining
                and not conditions.is_snowing
                and not conditions.is_thunderstorm
            ):
                self.systems.append(BirdSystem())
        else:
            self.systems.append(StarSystem())
            self.systems.append(MoonSystem(moon_phase))

        # ---- weather-specific ----
        if conditions.is_raining:
            self.systems.append(RainSystem(conditions.rain_intensity))
        elif conditions.is_snowing:
            self.systems.append(SnowSystem(conditions.snow_intensity))

        if conditions.is_thunderstorm:
            self.systems.append(ThunderstormSystem())

        if conditions.is_foggy:
            self.systems.append(FogSystem())

        if not conditions.is_raining and not conditions.is_thunderstorm:
            self.systems.append(ChimneySmoke())

    # ------------------------------------------------------------------
    # per-frame tick
    # ------------------------------------------------------------------

    def step_frame(self, conditions: Conditions) -> None:
        """Advance every active system by one frame."""
        self._conditions = conditions
        for sys in self.systems:
            if sys.is_active(conditions):
                sys.step()

    def render_all(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:
        """Draw every active system onto *grid* (overwrites existing cells)."""
        cond = self._conditions
        if cond is None:
            return
        for sys in self.systems:
            if sys.is_active(cond):
                sys.render(grid)
