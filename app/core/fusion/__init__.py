"""Multimodal Fusion Module."""

from app.core.fusion.multimodal_fusion import (
    ModalityFeatures,
    EarlyFusion,
    LateFusion,
    AttentionFusion,
    CrossModalAttention,
    MultimodalClassifier,
)

__all__ = [
    "ModalityFeatures",
    "EarlyFusion",
    "LateFusion", 
    "AttentionFusion",
    "CrossModalAttention",
    "MultimodalClassifier",
]
