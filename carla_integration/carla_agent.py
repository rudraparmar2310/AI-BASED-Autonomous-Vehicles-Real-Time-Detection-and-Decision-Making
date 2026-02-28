"""
CARLA simulator agent.

This module provides :class:`CarlaAgent`, which:

1. Connects to a running CARLA server.
2. Spawns an ego vehicle and attaches an RGB camera sensor.
3. Runs the perception–decision loop:
   - Each camera frame is passed to :class:`~detection.detector.YOLOv8Detector`.
   - Detections are scored by :class:`~decision.risk_scorer.RiskScorer`.
   - The :class:`~decision.decision_maker.DecisionMaker` produces a command.
   - The command is translated into CARLA vehicle controls.

CARLA Python API (``carla``) is imported lazily so the rest of the codebase
remains importable without a CARLA installation.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

import numpy as np

from decision.decision_maker import DecisionMaker, DrivingCommand
from decision.risk_scorer import RiskScorer
from detection.detector import YOLOv8Detector

logger = logging.getLogger(__name__)


def _import_carla():
    """Lazy import of the CARLA Python package."""
    try:
        import carla  # noqa: PLC0415
        return carla
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "The CARLA Python package is not installed. "
            "Follow the CARLA installation guide at https://carla.readthedocs.io/"
        ) from exc


class CarlaAgent:
    """Autonomous agent that runs inside the CARLA simulator.

    Args:
        host (str): CARLA server hostname (default ``"localhost"``).
        port (int): CARLA server port (default ``2000``).
        detector (YOLOv8Detector): Pre-configured detector instance.
        risk_scorer (RiskScorer): Pre-configured risk scorer.
        decision_maker (DecisionMaker): Pre-configured decision maker.
        camera_width (int): RGB camera resolution width.
        camera_height (int): RGB camera resolution height.
        target_speed_kmh (float): Cruise speed when command is GO.
        slow_speed_kmh (float): Speed when command is SLOW.
        timeout (float): CARLA client timeout in seconds.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 2000,
        detector: Optional[YOLOv8Detector] = None,
        risk_scorer: Optional[RiskScorer] = None,
        decision_maker: Optional[DecisionMaker] = None,
        camera_width: int = 1280,
        camera_height: int = 720,
        target_speed_kmh: float = 50.0,
        slow_speed_kmh: float = 15.0,
        timeout: float = 10.0,
    ) -> None:
        self.host = host
        self.port = port
        self.detector = detector or YOLOv8Detector(focal_length_px=800.0)
        self.risk_scorer = risk_scorer or RiskScorer(image_width=camera_width)
        self.decision_maker = decision_maker or DecisionMaker()
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.target_speed_kmh = target_speed_kmh
        self.slow_speed_kmh = slow_speed_kmh
        self.timeout = timeout

        # CARLA objects – populated during connect()
        self._client = None
        self._world = None
        self._vehicle = None
        self._camera = None
        self._latest_frame: Optional[np.ndarray] = None

    # ------------------------------------------------------------------
    # Connection & setup
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Connect to the CARLA server and retrieve the world."""
        carla = _import_carla()
        self._client = carla.Client(self.host, self.port)
        self._client.set_timeout(self.timeout)
        self._world = self._client.get_world()
        logger.info("Connected to CARLA server at %s:%d", self.host, self.port)

    def spawn_vehicle(self, vehicle_filter: str = "vehicle.tesla.model3") -> None:
        """Spawn the ego vehicle at a random recommended spawn point."""
        carla = _import_carla()
        bp_lib = self._world.get_blueprint_library()
        vehicle_bp = bp_lib.filter(vehicle_filter)[0]
        spawn_points = self._world.get_map().get_spawn_points()
        if not spawn_points:
            raise RuntimeError("No spawn points found in the current CARLA map.")
        self._vehicle = self._world.spawn_actor(vehicle_bp, spawn_points[0])
        logger.info("Spawned vehicle: %s", vehicle_filter)

    def attach_camera(self) -> None:
        """Attach an RGB camera sensor to the ego vehicle."""
        carla = _import_carla()
        bp_lib = self._world.get_blueprint_library()
        camera_bp = bp_lib.find("sensor.camera.rgb")
        camera_bp.set_attribute("image_size_x", str(self.camera_width))
        camera_bp.set_attribute("image_size_y", str(self.camera_height))
        camera_bp.set_attribute("fov", "90")

        transform = carla.Transform(carla.Location(x=2.5, z=1.5))
        self._camera = self._world.spawn_actor(
            camera_bp, transform, attach_to=self._vehicle
        )
        self._camera.listen(self._on_camera_image)
        logger.info(
            "Camera attached (%dx%d)", self.camera_width, self.camera_height
        )

    def _on_camera_image(self, image) -> None:
        """Callback: convert CARLA raw image to an OpenCV-compatible array."""
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = array.reshape((image.height, image.width, 4))
        self._latest_frame = array[:, :, :3]  # Drop alpha channel

    # ------------------------------------------------------------------
    # Control translation
    # ------------------------------------------------------------------

    def _apply_command(self, command: DrivingCommand) -> None:
        """Translate a :class:`~decision.decision_maker.DrivingCommand` into CARLA controls."""
        carla = _import_carla()
        control = carla.VehicleControl()

        if command == DrivingCommand.STOP:
            control.throttle = 0.0
            control.brake = 1.0
            control.steer = 0.0
        elif command == DrivingCommand.SLOW:
            # Check current speed and apply gentle throttle/brake
            vel = self._vehicle.get_velocity()
            speed_kmh = 3.6 * (vel.x**2 + vel.y**2 + vel.z**2) ** 0.5
            if speed_kmh > self.slow_speed_kmh:
                control.throttle = 0.0
                control.brake = 0.4
            else:
                control.throttle = 0.2
                control.brake = 0.0
            control.steer = 0.0
        else:  # GO
            vel = self._vehicle.get_velocity()
            speed_kmh = 3.6 * (vel.x**2 + vel.y**2 + vel.z**2) ** 0.5
            if speed_kmh < self.target_speed_kmh:
                control.throttle = 0.6
                control.brake = 0.0
            else:
                control.throttle = 0.0
                control.brake = 0.1
            control.steer = 0.0

        self._vehicle.apply_control(control)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self, duration_s: float = 60.0, tick_rate_hz: float = 10.0) -> None:
        """Run the perception–decision–control loop.

        Args:
            duration_s: How long to run (seconds).
            tick_rate_hz: Target loop frequency in Hz.
        """
        self.connect()
        self.spawn_vehicle()
        self.attach_camera()

        tick_interval = 1.0 / tick_rate_hz
        end_time = time.time() + duration_s
        logger.info("Starting agent loop for %.1f seconds.", duration_s)

        try:
            while time.time() < end_time:
                loop_start = time.time()

                if self._latest_frame is not None:
                    frame = self._latest_frame.copy()

                    # Perception
                    detections = self.detector.detect(frame)

                    # Risk scoring
                    risk_scores = self.risk_scorer.score(detections)

                    # Decision
                    decision = self.decision_maker.decide(risk_scores)
                    logger.debug("Decision: %s | %s", decision.command.value, decision.reason)

                    # Control
                    self._apply_command(decision.command)

                elapsed = time.time() - loop_start
                sleep_time = tick_interval - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
        finally:
            self.cleanup()

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """Destroy CARLA actors and disconnect."""
        if self._camera is not None:
            self._camera.stop()
            self._camera.destroy()
            self._camera = None
        if self._vehicle is not None:
            self._vehicle.destroy()
            self._vehicle = None
        logger.info("CARLA agent cleaned up.")
