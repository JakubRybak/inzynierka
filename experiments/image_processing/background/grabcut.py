"""Foreground masking with GrabCut."""

import cv2
import numpy as np
from PIL import Image


def grabcut_mask(image):
    """Seed GrabCut with the studio background color sampled from the side edges."""
    width, height = image.size
    scale = 512 / max(width, height)
    size = (round(width * scale), round(height * scale))
    rgb = np.asarray(image.resize(size, Image.Resampling.LANCZOS))
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    edge = np.concatenate((lab[:, :8], lab[:, -8:]), axis=1)
    background = np.median(edge.reshape(-1, 3), axis=0)
    distance = np.linalg.norm(lab - background, axis=2)

    labels = np.full(distance.shape, cv2.GC_PR_BGD, dtype=np.uint8)
    labels[distance > 16] = cv2.GC_PR_FGD
    labels[distance > 38] = cv2.GC_FGD
    labels[:, :3] = cv2.GC_BGD
    labels[:, -3:] = cv2.GC_BGD
    models = [np.zeros((1, 65), dtype=np.float64) for _ in range(2)]
    cv2.grabCut(rgb, labels, None, *models, 4, cv2.GC_INIT_WITH_MASK)
    foreground = (labels % 2).astype(np.uint8)
    count, components, stats, _ = cv2.connectedComponentsWithStats(foreground)
    if count < 2:
        raise ValueError("No foreground component detected")
    largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    mask = (components == largest).astype(np.uint8) * 255
    mask = cv2.GaussianBlur(mask, (5, 5), 0.9)
    return Image.fromarray(mask).resize(image.size, Image.Resampling.BILINEAR)
