"""
WIoU (Wise Intersection over Union) loss for YOLOv8 bounding-box regression.

Reference: "WIoU: Bounding Box Regression Loss with Dynamic Focusing Mechanism"
(Tong et al., 2023).

The loss introduces a *focusing coefficient* β that down-weights well-fitting
anchor boxes so training concentrates on harder, low-quality examples, which
improves small-object and occluded-object detection – both common in autonomous
driving scenarios.
"""

import torch
import torch.nn as nn


class WIoULoss(nn.Module):
    """Wise IoU (WIoU v3) bounding-box regression loss.

    Args:
        scale (float): Scaling factor for the Wise gradient gain (default 1.0).
        monotonic_focal (bool): When *True* use the monotonic focusing
            coefficient (WIoU v3); when *False* fall back to the simpler
            constant-weight version (WIoU v1).
        eps (float): Small value for numerical stability.
    """

    def __init__(
        self,
        scale: float = 1.0,
        monotonic_focal: bool = True,
        eps: float = 1e-7,
    ) -> None:
        super().__init__()
        self.scale = scale
        self.monotonic_focal = monotonic_focal
        self.eps = eps

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _box_iou(pred: torch.Tensor, target: torch.Tensor, eps: float = 1e-7) -> torch.Tensor:
        """Compute element-wise IoU between *pred* and *target*.

        Both tensors are in (cx, cy, w, h) format.
        """
        # Convert to (x1, y1, x2, y2)
        p_x1 = pred[:, 0] - pred[:, 2] / 2
        p_y1 = pred[:, 1] - pred[:, 3] / 2
        p_x2 = pred[:, 0] + pred[:, 2] / 2
        p_y2 = pred[:, 1] + pred[:, 3] / 2

        t_x1 = target[:, 0] - target[:, 2] / 2
        t_y1 = target[:, 1] - target[:, 3] / 2
        t_x2 = target[:, 0] + target[:, 2] / 2
        t_y2 = target[:, 1] + target[:, 3] / 2

        inter_x1 = torch.max(p_x1, t_x1)
        inter_y1 = torch.max(p_y1, t_y1)
        inter_x2 = torch.min(p_x2, t_x2)
        inter_y2 = torch.min(p_y2, t_y2)

        inter_area = (inter_x2 - inter_x1).clamp(min=0) * (inter_y2 - inter_y1).clamp(min=0)
        pred_area = (p_x2 - p_x1) * (p_y2 - p_y1)
        tgt_area = (t_x2 - t_x1) * (t_y2 - t_y1)
        union_area = pred_area + tgt_area - inter_area + eps

        return inter_area / union_area

    @staticmethod
    def _normalised_distance(
        pred: torch.Tensor, target: torch.Tensor, eps: float = 1e-7
    ) -> torch.Tensor:
        """Compute the normalised centre-point distance used by WIoU.

        Returns ρ² / c², where ρ is the Euclidean distance between centres and
        c is the diagonal length of the smallest enclosing box.
        """
        rho2 = (pred[:, 0] - target[:, 0]) ** 2 + (pred[:, 1] - target[:, 1]) ** 2

        # Enclosing box
        p_x1 = pred[:, 0] - pred[:, 2] / 2
        p_y1 = pred[:, 1] - pred[:, 3] / 2
        p_x2 = pred[:, 0] + pred[:, 2] / 2
        p_y2 = pred[:, 1] + pred[:, 3] / 2

        t_x1 = target[:, 0] - target[:, 2] / 2
        t_y1 = target[:, 1] - target[:, 3] / 2
        t_x2 = target[:, 0] + target[:, 2] / 2
        t_y2 = target[:, 1] + target[:, 3] / 2

        enc_w = torch.max(p_x2, t_x2) - torch.min(p_x1, t_x1)
        enc_h = torch.max(p_y2, t_y2) - torch.min(p_y1, t_y1)
        c2 = enc_w ** 2 + enc_h ** 2 + eps

        return rho2 / c2

    # ------------------------------------------------------------------
    # Forward
    # ------------------------------------------------------------------

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Compute WIoU loss.

        Args:
            pred (Tensor): Predicted boxes ``(N, 4)`` in (cx, cy, w, h) format.
            target (Tensor): Ground-truth boxes ``(N, 4)`` in (cx, cy, w, h) format.

        Returns:
            Tensor: Scalar loss value.
        """
        iou = self._box_iou(pred, target, self.eps)
        dist = self._normalised_distance(pred, target, self.eps)

        # WIoU base loss (DIoU-like)
        wiou_base = 1.0 - iou + dist

        if self.monotonic_focal:
            # WIoU v3: focusing coefficient β = exp((iou - iou_mean) / δ)
            # δ is controlled by *scale*; using a detached mean so gradients
            # do not flow through the coefficient itself.
            iou_mean = iou.detach().mean().clamp(min=self.eps)
            delta = self.scale * iou_mean
            beta = torch.exp((iou.detach() - iou_mean) / delta)
            loss = (beta * wiou_base).mean()
        else:
            loss = wiou_base.mean()

        return loss
