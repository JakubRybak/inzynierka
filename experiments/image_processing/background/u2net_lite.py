"""Foreground masking with U²-Net Lite."""

import cv2
import numpy as np
from PIL import Image


def load_model(weights):
    return cv2.dnn.readNetFromONNX(str(weights))


def predict_mask(network, image):
    rgb = np.asarray(image.resize((320, 320), Image.Resampling.BILINEAR), dtype=np.float32)
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    tensor = ((rgb / 255 - mean) / std).transpose(2, 0, 1)[None]
    network.setInput(tensor)
    prediction = network.forward(network.getUnconnectedOutLayersNames())[0].squeeze()
    return Image.fromarray(np.uint8(np.clip(prediction, 0, 1) * 255)).resize(
        image.size, Image.Resampling.BILINEAR
    )
