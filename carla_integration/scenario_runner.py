"""
CARLA scenario runner for complex traffic scenario validation.

Provides :class:`ScenarioRunner`, which programmatically creates traffic
scenarios in CARLA to validate the perception–decision system under:

* Dense urban traffic
* Pedestrian crossings
* Emergency vehicle encounters
* Adverse weather conditions (rain, fog, night)
"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

logger = logging.getLogger(__name__)


class WeatherPreset(Enum):
    """Named weather presets for CARLA simulation."""

    CLEAR_NOON = "ClearNoon"
    CLOUDY_NOON = "CloudyNoon"
    WET_NOON = "WetNoon"
    HARD_RAIN_NOON = "HardRainNoon"
    CLEAR_SUNSET = "ClearSunset"
    CLEAR_NIGHT = "ClearNight"
    HARD_RAIN_NIGHT = "HardRainNight"
    SOFT_RAIN_NOON = "SoftRainNoon"


@dataclass
class ScenarioConfig:
    """Configuration for a single test scenario.

    Attributes:
        name (str): Human-readable scenario identifier.
        num_vehicles (int): Number of NPC vehicles to spawn.
        num_pedestrians (int): Number of NPC pedestrians to spawn.
        weather (WeatherPreset): Weather preset.
        duration_s (float): Scenario duration in seconds.
        spawn_radius_m (float): Radius around the ego vehicle for NPC spawning.
        tags (list[str]): Free-form tags for classification.
    """

    name: str
    num_vehicles: int = 20
    num_pedestrians: int = 10
    weather: WeatherPreset = WeatherPreset.CLEAR_NOON
    duration_s: float = 60.0
    spawn_radius_m: float = 80.0
    tags: List[str] = field(default_factory=list)


# Pre-defined complex traffic scenarios as described in the problem statement
PREDEFINED_SCENARIOS: List[ScenarioConfig] = [
    ScenarioConfig(
        name="dense_urban_traffic",
        num_vehicles=40,
        num_pedestrians=20,
        weather=WeatherPreset.CLEAR_NOON,
        duration_s=120.0,
        tags=["urban", "dense", "complex"],
    ),
    ScenarioConfig(
        name="pedestrian_crossing",
        num_vehicles=5,
        num_pedestrians=30,
        weather=WeatherPreset.CLEAR_NOON,
        duration_s=60.0,
        tags=["pedestrian", "safety-critical"],
    ),
    ScenarioConfig(
        name="heavy_rain_night",
        num_vehicles=20,
        num_pedestrians=10,
        weather=WeatherPreset.HARD_RAIN_NIGHT,
        duration_s=90.0,
        tags=["adverse-weather", "night", "visibility"],
    ),
    ScenarioConfig(
        name="soft_rain_noon",
        num_vehicles=15,
        num_pedestrians=8,
        weather=WeatherPreset.SOFT_RAIN_NOON,
        duration_s=90.0,
        tags=["adverse-weather", "rain", "visibility"],
    ),
    ScenarioConfig(
        name="highway_overtake",
        num_vehicles=25,
        num_pedestrians=0,
        weather=WeatherPreset.CLEAR_SUNSET,
        duration_s=60.0,
        tags=["highway", "speed"],
    ),
]


class ScenarioRunner:
    """Orchestrate complex traffic scenarios in CARLA.

    Args:
        agent: A connected :class:`~carla_integration.carla_agent.CarlaAgent`.
            The agent should already have called ``connect()`` before
            ``ScenarioRunner`` methods are invoked.
        seed (int | None): Random seed for reproducible NPC placement.
    """

    def __init__(self, agent, seed: Optional[int] = None) -> None:
        self.agent = agent
        self.seed = seed
        self._npc_vehicles: list = []
        self._npc_pedestrians: list = []
        if seed is not None:
            random.seed(seed)

    # ------------------------------------------------------------------
    # Scenario lifecycle
    # ------------------------------------------------------------------

    def _set_weather(self, preset: WeatherPreset) -> None:
        """Apply a weather preset to the CARLA world."""
        try:
            carla = self.agent._world  # noqa: SLF001
            weather = getattr(
                __import__("carla").WeatherParameters,
                preset.value,
                None,
            )
            if weather is not None:
                self.agent._world.set_weather(weather)  # noqa: SLF001
                logger.info("Weather set to %s", preset.value)
        except Exception:  # pragma: no cover – CARLA not present in CI
            logger.warning("Could not set weather preset %s.", preset.value)

    def _spawn_npcs(self, config: ScenarioConfig) -> None:
        """Spawn NPC vehicles and pedestrians according to *config*."""
        try:
            import carla  # noqa: PLC0415
            world = self.agent._world  # noqa: SLF001
            bp_lib = world.get_blueprint_library()
            spawn_points = world.get_map().get_spawn_points()

            # NPC Vehicles
            vehicle_bps = bp_lib.filter("vehicle.*")
            for _ in range(min(config.num_vehicles, len(spawn_points))):
                bp = random.choice(vehicle_bps)
                sp = random.choice(spawn_points)
                try:
                    npc = world.spawn_actor(bp, sp)
                    npc.set_autopilot(True)
                    self._npc_vehicles.append(npc)
                except Exception:  # noqa: BLE001
                    pass

            # NPC Pedestrians
            walker_bps = bp_lib.filter("walker.pedestrian.*")
            walker_controller_bp = bp_lib.find("controller.ai.walker")
            for _ in range(config.num_pedestrians):
                bp = random.choice(walker_bps)
                loc = world.get_random_location_from_navigation()
                if loc is None:
                    continue
                transform = carla.Transform(loc)
                try:
                    walker = world.spawn_actor(bp, transform)
                    controller = world.spawn_actor(
                        walker_controller_bp,
                        carla.Transform(),
                        attach_to=walker,
                    )
                    controller.start()
                    controller.go_to_location(world.get_random_location_from_navigation())
                    self._npc_pedestrians.append((walker, controller))
                except Exception:  # noqa: BLE001
                    pass

            logger.info(
                "Spawned %d NPC vehicles and %d pedestrians.",
                len(self._npc_vehicles),
                len(self._npc_pedestrians),
            )
        except ImportError:  # pragma: no cover
            logger.warning("CARLA not available; skipping NPC spawning.")

    def _cleanup_npcs(self) -> None:
        """Destroy all spawned NPC actors."""
        for walker, controller in self._npc_pedestrians:
            try:
                controller.stop()
                controller.destroy()
                walker.destroy()
            except Exception:  # noqa: BLE001
                pass
        self._npc_pedestrians.clear()

        for npc in self._npc_vehicles:
            try:
                npc.destroy()
            except Exception:  # noqa: BLE001
                pass
        self._npc_vehicles.clear()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_scenario(self, config: ScenarioConfig) -> None:
        """Execute a single scenario.

        Args:
            config: :class:`ScenarioConfig` describing the scenario parameters.
        """
        logger.info("Starting scenario: %s", config.name)
        self._set_weather(config.weather)
        self._spawn_npcs(config)

        try:
            self.agent.run(duration_s=config.duration_s)
        finally:
            self._cleanup_npcs()
            logger.info("Scenario '%s' complete.", config.name)

    def run_all_predefined(self) -> None:
        """Run all :data:`PREDEFINED_SCENARIOS` sequentially."""
        for scenario in PREDEFINED_SCENARIOS:
            self.run_scenario(scenario)
            time.sleep(2.0)  # Brief pause between scenarios
