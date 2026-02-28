"""
Main entry point for the AI-Based Autonomous Vehicles
Real-Time Detection and Decision-Making system.

Usage
-----
Run against a CARLA simulator::

    python main.py --mode carla --host localhost --port 2000 --duration 120

Run against a video file for offline testing::

    python main.py --mode video --source path/to/video.mp4

Run a single image for quick testing::

    python main.py --mode image --source path/to/image.jpg
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mode handlers
# ---------------------------------------------------------------------------

def run_carla_mode(args: argparse.Namespace) -> None:
    """Launch the agent inside the CARLA simulator."""
    from carla_integration.carla_agent import CarlaAgent
    from decision.decision_maker import DecisionMaker
    from decision.risk_scorer import RiskScorer
    from detection.detector import YOLOv8Detector

    detector = YOLOv8Detector(
        model_path=args.model,
        conf_threshold=args.conf,
        focal_length_px=args.focal_length,
        device=args.device,
    )
    risk_scorer = RiskScorer(image_width=args.camera_width)
    decision_maker = DecisionMaker(
        stop_threshold=args.stop_threshold,
        slow_threshold=args.slow_threshold,
    )

    agent = CarlaAgent(
        host=args.host,
        port=args.port,
        detector=detector,
        risk_scorer=risk_scorer,
        decision_maker=decision_maker,
        camera_width=args.camera_width,
        camera_height=args.camera_height,
    )
    agent.run(duration_s=args.duration)


def run_video_mode(args: argparse.Namespace) -> None:
    """Process a video file frame-by-frame."""
    try:
        import cv2  # noqa: PLC0415
    except ImportError:
        logger.error("opencv-python is required for video mode.")
        sys.exit(1)

    from decision.decision_maker import DecisionMaker
    from decision.risk_scorer import RiskScorer
    from detection.detector import YOLOv8Detector
    from utils.visualization import Visualizer

    detector = YOLOv8Detector(
        model_path=args.model,
        conf_threshold=args.conf,
        focal_length_px=args.focal_length,
        device=args.device,
    )
    risk_scorer = RiskScorer(image_width=args.camera_width)
    decision_maker = DecisionMaker(
        stop_threshold=args.stop_threshold,
        slow_threshold=args.slow_threshold,
    )
    visualizer = Visualizer(
        slow_threshold=args.slow_threshold,
        stop_threshold=args.stop_threshold,
    )

    cap = cv2.VideoCapture(str(args.source))
    if not cap.isOpened():
        logger.error("Cannot open video source: %s", args.source)
        sys.exit(1)

    # Set up optional video writer
    writer = None
    if args.output:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(str(args.output), fourcc, fps, (w, h))

    frame_idx = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            detections = detector.detect(frame)
            risk_scores = risk_scorer.score(detections)
            decision = decision_maker.decide(risk_scores)

            annotated = visualizer.draw(frame, risk_scores, decision.command.value)

            if writer:
                writer.write(annotated)

            if args.display:
                cv2.imshow("Autonomous Driving Perception", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            frame_idx += 1
            if frame_idx % 30 == 0:
                logger.info(
                    "Frame %d | Command: %s | Max risk: %.3f",
                    frame_idx,
                    decision.command.value,
                    decision.max_risk_score,
                )
    finally:
        cap.release()
        if writer:
            writer.release()
        if args.display:
            cv2.destroyAllWindows()

    logger.info("Processed %d frames.", frame_idx)


def run_image_mode(args: argparse.Namespace) -> None:
    """Process a single image."""
    try:
        import cv2  # noqa: PLC0415
    except ImportError:
        logger.error("opencv-python is required for image mode.")
        sys.exit(1)

    from decision.decision_maker import DecisionMaker
    from decision.risk_scorer import RiskScorer
    from detection.detector import YOLOv8Detector
    from utils.visualization import Visualizer

    frame = cv2.imread(str(args.source))
    if frame is None:
        logger.error("Cannot read image: %s", args.source)
        sys.exit(1)

    detector = YOLOv8Detector(
        model_path=args.model,
        conf_threshold=args.conf,
        focal_length_px=args.focal_length,
        device=args.device,
    )
    risk_scorer = RiskScorer(image_width=frame.shape[1])
    decision_maker = DecisionMaker(
        stop_threshold=args.stop_threshold,
        slow_threshold=args.slow_threshold,
    )
    visualizer = Visualizer(
        slow_threshold=args.slow_threshold,
        stop_threshold=args.stop_threshold,
    )

    detections = detector.detect(frame)
    risk_scores = risk_scorer.score(detections)
    decision = decision_maker.decide(risk_scores)

    annotated = visualizer.draw(frame, risk_scores, decision.command.value)

    logger.info(
        "Image: %d detections | Command: %s | Max risk: %.3f",
        len(detections),
        decision.command.value,
        decision.max_risk_score,
    )

    if args.output:
        cv2.imwrite(str(args.output), annotated)
        logger.info("Saved annotated image to %s", args.output)

    if args.display:
        cv2.imshow("Detection Result", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "AI-Based Autonomous Vehicles Real-Time Detection and Decision-Making\n"
            "Perception system using YOLOv8 (WIoU-optimised) with CARLA integration."
        )
    )

    parser.add_argument(
        "--mode",
        choices=["carla", "video", "image"],
        default="image",
        help="Operating mode (default: image).",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Path to input image or video file (required for 'image' and 'video' modes).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path to save the annotated output.",
    )
    parser.add_argument(
        "--model",
        default="yolov8n.pt",
        help="YOLOv8 model weights (default: yolov8n.pt).",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.4,
        help="Detection confidence threshold (default: 0.4).",
    )
    parser.add_argument(
        "--stop-threshold",
        type=float,
        default=0.65,
        help="Risk score threshold for STOP command (default: 0.65).",
    )
    parser.add_argument(
        "--slow-threshold",
        type=float,
        default=0.30,
        help="Risk score threshold for SLOW command (default: 0.30).",
    )
    parser.add_argument(
        "--focal-length",
        type=float,
        default=None,
        help="Camera focal length in pixels for distance estimation.",
    )
    parser.add_argument(
        "--camera-width",
        type=int,
        default=1280,
        help="Camera frame width in pixels (default: 1280).",
    )
    parser.add_argument(
        "--camera-height",
        type=int,
        default=720,
        help="Camera frame height in pixels (default: 720).",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="PyTorch device string, e.g. 'cpu' or 'cuda' (default: cpu).",
    )
    parser.add_argument(
        "--display",
        action="store_true",
        help="Show annotated frames in a window (requires a display).",
    )

    # CARLA-specific arguments
    carla_group = parser.add_argument_group("CARLA options")
    carla_group.add_argument(
        "--host",
        default="localhost",
        help="CARLA server hostname (default: localhost).",
    )
    carla_group.add_argument(
        "--port",
        type=int,
        default=2000,
        help="CARLA server port (default: 2000).",
    )
    carla_group.add_argument(
        "--duration",
        type=float,
        default=60.0,
        help="CARLA simulation duration in seconds (default: 60).",
    )

    return parser


def main(argv: list | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.mode in ("video", "image") and args.source is None:
        parser.error(f"--source is required for mode '{args.mode}'.")

    if args.mode == "carla":
        run_carla_mode(args)
    elif args.mode == "video":
        run_video_mode(args)
    else:
        run_image_mode(args)


if __name__ == "__main__":
    main()
