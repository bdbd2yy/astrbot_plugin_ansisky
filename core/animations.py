"""Animation systems for ANSI Sky weather plugin.

Provides particle/effect systems and an AnimationController that orchestrates
them based on weather conditions, time of day, and moon phase.

Grid convention: cells are (char, (r,g,b)) tuples accessed as grid[y][x].
Dimensions: 114 columns x 45 rows. Ground level is at row 38.
"""

from __future__ import annotations

import random
from typing import Optional

from .weather_codes import Conditions, WeatherCondition

# ── Grid dimensions ──────────────────────────────────────────────────────────

COLS: int = 114
ROWS: int = 45
Y_GROUND: int = 38

# ── Colour palette ───────────────────────────────────────────────────────────

STAR_COLOR: tuple[int, int, int] = (210, 215, 235)
MOON_COLOR: tuple[int, int, int] = (176, 184, 208)
MOON_FILL_COLOR: tuple[int, int, int] = (31, 31, 47)
SUN_COLOR: tuple[int, int, int] = (225, 210, 145)
CLOUD_COLOR: tuple[int, int, int] = (200, 200, 210)
BIRD_COLOR: tuple[int, int, int] = (80, 80, 80)
RAIN_COLOR: tuple[int, int, int] = (173, 216, 230)
SNOW_COLOR: tuple[int, int, int] = (255, 250, 250)
LIGHTNING_COLOR: tuple[int, int, int] = (255, 255, 100)
FOG_COLOR: tuple[int, int, int] = (200, 200, 200)
SMOKE_COLOR: tuple[int, int, int] = (180, 180, 180)

# ── Cloud shapes ─────────────────────────────────────────────────────────────

CLOUD_SHAPES: list[list[str]] = [
    ["    __   __    ", "  _(  )_(  )_  "],
    ["   ___  ___   ", "  (   )(   )  "],
    ["    _____    ", "  _(     )_  "],
    ["   __  __   ", "  (  )(  )  "],
    ["  ___  ___  ___  ", " (   )(   )(   ) "],
    ["   ______   ", " _(      )_ "],
]

# ── Particle character sets ──────────────────────────────────────────────────

RAIN_CHARS: list[str] = ["|", "|", "|", "|", "|", "│", "╎", "╏"]
SNOW_CHARS: list[str] = ["*", ".", "+", "·", "*", "."]
BIRD_CHARS: list[str] = ["v", "^"]
STAR_CHARSET: list[str] = [".", "·", "*", "·", "."]
FOG_CHARS: list[str] = ["~", "~", "~", "≈", "∽", "░"]

# ── Position ranges ──────────────────────────────────────────────────────────

CLOUD_Y_MIN: int = 3
CLOUD_Y_MAX: int = 25
BIRD_Y_MIN: int = 5
BIRD_Y_MAX: int = 30
FOG_Y_MIN: int = 8
FOG_Y_MAX: int = 30
STAR_Y_MIN: int = 1
STAR_Y_MAX: int = 28

# ── Lightning range ──────────────────────────────────────────────────────────

LIGHTNING_X_MIN: int = 30
LIGHTNING_X_MAX: int = 85

# ── Chimney position ─────────────────────────────────────────────────────────

CHIMNEY_X: int = 37
CHIMNEY_Y: int = 28

# ── Particle counts ──────────────────────────────────────────────────────────

RAIN_COUNTS: dict[str, int] = {"light": 35, "moderate": 70, "heavy": 105}
SNOW_COUNTS: dict[str, int] = {"light": 35, "medium": 50, "heavy": 85}


# ── Helper ───────────────────────────────────────────────────────────────────

def _in_bounds(x: int, y: int) -> bool:
    return 0 <= x < COLS and 0 <= y < ROWS


# ═══════════════════════════════════════════════════════════════════════════════
# Base class
# ═══════════════════════════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════════════════════════
# 1. StarSystem
# ═══════════════════════════════════════════════════════════════════════════════


class StarSystem(AnimationSystem):
    """100 twinkling stars in the upper sky (rows STAR_Y_MIN to STAR_Y_MAX).

    Always active; the controller adds it only at night.
    """

    def __init__(self) -> None:
        self._stars: list[dict] = []
        for _ in range(100):
            self._stars.append({
                "x": random.randint(0, COLS - 1),
                "y": random.randint(STAR_Y_MIN, STAR_Y_MAX),
                "bright": random.choice([True, False]),
            })

    def step(self) -> None:
        # twinkle ~10% of stars each frame
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


# ═══════════════════════════════════════════════════════════════════════════════
# 2. MoonSystem — weathr full moon
# ═══════════════════════════════════════════════════════════════════════════════


class MoonSystem(AnimationSystem):
    """Static full moon using weathr's phase_4 ASCII art."""

    MOON_X: int = 84
    MOON_Y: int = 10

    _MOON_ART: tuple[str, ...] = (
        "       _..._      ",
        "     .'~o~~~`.    ",
        "    :~~~~~o~~~:   ",
        "    :~~o~~~~.~:   ",
        "    `.~~~~~o~.'   ",
        "      `-...-'     ",
    )

    def __init__(self, moon_phase: float = 0.5) -> None:
        self.moon_phase: float = moon_phase

    def step(self) -> None:
        pass  # static — no animation

    def render(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:
        for row_offset, line in enumerate(self._MOON_ART):
            y = self.MOON_Y + row_offset
            for col_offset, ch in enumerate(line):
                x = self.MOON_X + col_offset
                if not _in_bounds(x, y) or ch == " ":
                    continue
                color = MOON_FILL_COLOR if ch == "~" else MOON_COLOR
                grid[y][x] = (ch, color)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. SunSystem — weathr two-frame sun
# ═══════════════════════════════════════════════════════════════════════════════


class SunSystem(AnimationSystem):
    """Animated line-art sun from weathr's sun_0/sun_1 assets."""

    SUN_X: int = 46
    SUN_Y: int = 3

    _FRAMES: tuple[tuple[str, ...], ...] = (
        (
            "      ;   :   ;",
            "   .   \\_,!,_/   ,",
            "    `.,'     `.,'",
            "     /         \\",
            "~ -- :         : -- ~",
            "     \\         /",
            "    ,'`._   _.'`.",
            "   '   / `!` \\   `",
            "      ;   :   ;",
        ),
        (
            "      .   |   .",
            "   ;   \\_,|,_/   ;",
            "    `.,'     `.,'",
            "     /         \\",
            "~ -- |         | -- ~",
            "     \\         /",
            "    ,'`._   _.'`.",
            "   ;   / `|` \\   ;",
            "      .   |   .",
        ),
    )

    def __init__(self) -> None:
        self._frame: int = 0

    def step(self) -> None:
        self._frame = 1 - self._frame

    def render(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:
        for row_offset, line in enumerate(self._FRAMES[self._frame]):
            y = self.SUN_Y + row_offset
            for col_offset, ch in enumerate(line):
                x = self.SUN_X + col_offset
                if _in_bounds(x, y) and ch != " ":
                    grid[y][x] = (ch, SUN_COLOR)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CloudSystem
# ═══════════════════════════════════════════════════════════════════════════════


class CloudSystem(AnimationSystem):
    """Drifting multi-line clouds with varied, fluffy shapes.

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
                "y": random.randint(CLOUD_Y_MIN, CLOUD_Y_MAX),
                "shape": random.randint(0, len(CLOUD_SHAPES) - 1),
                "speed": random.uniform(0.3, 0.7),
            })

    def step(self) -> None:
        for cloud in self._clouds:
            cloud["x"] -= cloud["speed"]
            if cloud["x"] < -20:
                cloud["x"] = float(COLS)
                cloud["y"] = random.randint(CLOUD_Y_MIN, CLOUD_Y_MAX)
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


# ═══════════════════════════════════════════════════════════════════════════════
# 5. BirdSystem
# ═══════════════════════════════════════════════════════════════════════════════


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
                "y": random.randint(BIRD_Y_MIN, BIRD_Y_MAX),
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
                bird["y"] = random.randint(BIRD_Y_MIN, BIRD_Y_MAX)

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


# ═══════════════════════════════════════════════════════════════════════════════
# 6. RainSystem
# ═══════════════════════════════════════════════════════════════════════════════


class RainSystem(AnimationSystem):
    """Falling rain streaks at varying intensity.

    Particle count: light=35, moderate=70, heavy=105.
    """

    def __init__(self, intensity: str) -> None:
        self._target: int = RAIN_COUNTS.get(intensity, 40)
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


# ═══════════════════════════════════════════════════════════════════════════════
# 7. SnowSystem
# ═══════════════════════════════════════════════════════════════════════════════


class SnowSystem(AnimationSystem):
    """Falling snowflakes with gentle horizontal sway.

    Particle count: light=35, medium=50, heavy=85.
    """

    def __init__(self, intensity: str) -> None:
        self._target: int = SNOW_COUNTS.get(intensity, 30)
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


# ═══════════════════════════════════════════════════════════════════════════════
# 8. ThunderstormSystem
# ═══════════════════════════════════════════════════════════════════════════════


class ThunderstormSystem(AnimationSystem):
    """Lightning bolts that flash periodically.

    Generates 1-3 jagged bolts every 5-12 frames.
    Each flash persists for 2 frames.
    Bolts span x-range 30-85.
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
        x: float = float(random.randint(LIGHTNING_X_MIN, LIGHTNING_X_MAX))
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


# ═══════════════════════════════════════════════════════════════════════════════
# 9. FogSystem
# ═══════════════════════════════════════════════════════════════════════════════


class FogSystem(AnimationSystem):
    """Slowly drifting fog wisps (rows 8-30).

    Active only when conditions indicate fog.
    """

    def __init__(self) -> None:
        n_wisps = random.randint(6, 10)
        self._wisps: list[dict] = []
        for _ in range(n_wisps):
            self._wisps.append({
                "x": float(random.randint(0, COLS - 1)),
                "y": random.randint(FOG_Y_MIN, FOG_Y_MAX),
                "width": random.randint(3, 6),
                "char": random.choice(FOG_CHARS),
            })

    def is_active(self, conditions: Conditions) -> bool:
        return conditions.is_foggy

    def step(self) -> None:
        for wisp in self._wisps:
            wisp["x"] -= 0.5
            if wisp["x"] < -6:
                wisp["x"] = float(COLS)
                wisp["y"] = random.randint(FOG_Y_MIN, FOG_Y_MAX)

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
                    grid[y][x] = (wisp["char"], FOG_COLOR)


# ═══════════════════════════════════════════════════════════════════════════════
# 10. ChimneySmoke
# ═══════════════════════════════════════════════════════════════════════════════


class ChimneySmoke(AnimationSystem):
    """Thin smoke wisps rising from the weathr house chimney.

    Matches weathr's single-particle lifecycle: o -> . -> ~ -> ·, with a
    slow upward rise and subtle horizontal drift.

    Active only when it is not raining or storming.
    """

    MAX_PARTICLES: int = 24
    MIN_MAX_AGE: int = 70
    MAX_AGE_VARIANCE: int = 30
    SPAWN_RATE: int = 12
    VERTICAL_SPEED: float = 0.1
    DRIFT_SCALE: float = 0.08
    SPAWN_JITTER_X: float = 1.6

    def __init__(self) -> None:
        self._particles: list[dict] = [
            self._new_particle(age=age, drift=drift)
            for age, drift in ((4, -0.02), (18, 0.01), (32, -0.01), (50, 0.02))
        ]
        self._spawn_timer: int = 0

    def _new_particle(self, age: int = 0, drift: float | None = None) -> dict:
        if drift is None:
            drift = (random.random() - 0.5) * self.DRIFT_SCALE
        return {
            "x": CHIMNEY_X + (random.random() - 0.5) * self.SPAWN_JITTER_X,
            "y": float(CHIMNEY_Y) - age * self.VERTICAL_SPEED,
            "age": age,
            "max_age": self.MIN_MAX_AGE + random.randrange(self.MAX_AGE_VARIANCE),
            "drift": drift,
        }

    def is_active(self, conditions: Conditions) -> bool:
        return not conditions.is_raining and not conditions.is_thunderstorm

    def step(self) -> None:
        for p in self._particles:
            p["age"] += 1
            p["y"] -= self.VERTICAL_SPEED
            p["x"] += p["drift"]

        self._particles = [
            p for p in self._particles
            if p["age"] < p["max_age"] and p["y"] >= 0.0
        ]

        self._spawn_timer += 1
        if self._spawn_timer >= self.SPAWN_RATE and len(self._particles) < self.MAX_PARTICLES:
            self._spawn_timer = 0
            self._particles.append(self._new_particle())

    def render(
        self,
        grid: list[list[tuple[str, tuple[int, int, int]]]],
    ) -> None:
        for p in self._particles:
            x = int(p["x"])
            y = int(p["y"])
            if not _in_bounds(x, y):
                continue

            age = p["age"]
            if age <= 6:
                ch = "o"
            elif age <= 14:
                ch = "."
            elif age <= 25:
                ch = "~"
            else:
                ch = "·"

            life_ratio = age / p["max_age"]
            if life_ratio < 0.3:
                color = (235, 235, 235)
            elif life_ratio < 0.6:
                color = (160, 160, 170)
            else:
                color = (80, 80, 90)
            grid[y][x] = (ch, color)


# ═══════════════════════════════════════════════════════════════════════════════
# AnimationController
# ═══════════════════════════════════════════════════════════════════════════════


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
