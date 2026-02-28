"""
detection package – YOLOv8 detector with WIoU-optimised loss.
"""
from .wiou_loss import WIoULoss
from .detector import YOLOv8Detector

__all__ = ["WIoULoss", "YOLOv8Detector"]
