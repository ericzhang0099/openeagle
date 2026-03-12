"""Multimodal Fusion Module."""

from app.core.fusion.multimodal_fusion import (
    ModalityFeatures,
    EarlyFusion,
    LateFusion,
    AttentionFusion,
    CrossModalAttention,
    MultimodalClassifier,
)
from app.core.fusion.event_detection import (
    EventDetector,
    EventActionRecommender,
    DetectedEvent,
    EventType,
    EventSignature,
)

__all__ = [
    "ModalityFeatures",
    "EarlyFusion",
    "LateFusion", 
    "AttentionFusion",
    "CrossModalAttention",
    "MultimodalClassifier",
    "EventDetector",
    "EventActionRecommender",
    "DetectedEvent",
    "EventType",
    "EventSignature",
]
