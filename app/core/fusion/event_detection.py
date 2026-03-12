"""
Multimodal Event Detection System

Detects complex events by analyzing patterns across multiple modalities over time.

Examples:
- "Student getting frustrated": Frowning (vision) + Sighing (audio) + Pen tapping (temporal)
- "Loss of focus": Looking away (vision) + Silence (audio) + No hand movement (temporal)
- "Excitement breakthrough": Smiling (vision) + "Yes!" (audio) + Fast writing (temporal)

References:
- Complex Event Processing (CEP) patterns
- Multimodal fusion for behavioral analysis
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
from enum import Enum
import time

from app.core.fusion import ModalityFeatures, AttentionFusion
from app.utils.logger import logger


class EventType(Enum):
    """Types of detectable student events."""
    # Attention-related
    FOCUS_LOST = "focus_lost"           # 注意力涣散
    FOCUS_REGAINED = "focus_regained"   # 注意力恢复
    DEEP_FOCUS = "deep_focus"           # 深度专注
    
    # Emotional
    FRUSTRATION = "frustration"         # 沮丧/挫败
    EXCITEMENT = "excitement"           # 兴奋/突破
    CONFUSION = "confusion"             # 困惑
    SATISFACTION = "satisfaction"       # 满意
    
    # Physical
    FATIGUE = "fatigue"                 # 疲劳
    RESTLESSNESS = "restlessness"       # 坐立不安
    STRETCHING = "stretching"           # 伸展身体
    
    # Behavioral
    GIVING_UP = "giving_up"             # 放弃倾向
    PERSISTENCE = "persistence"         # 坚持不懈
    BREAKTHROUGH = "breakthrough"       # 突破时刻
    
    # Social
    ASKING_FOR_HELP = "asking_for_help" # 寻求帮助
    DISCUSSION_READY = "discussion_ready"  # 准备好讨论


@dataclass
class EventSignature:
    """Signature pattern for detecting an event."""
    event_type: EventType
    name: str
    description: str
    
    # Vision patterns
    vision_cues: List[str] = field(default_factory=list)
    # e.g., ["frowning", "looking_away", "smiling", "eye_rubbing"]
    
    # Audio patterns  
    audio_cues: List[str] = field(default_factory=list)
    # e.g., ["sighing", "silence", "yes_exclamation", "question_tone"]
    
    # Temporal/behavioral patterns
    temporal_cues: List[str] = field(default_factory=list)
    # e.g., ["pen_tapping", "no_movement", "fast_writing", "fidgeting"]
    
    # Required confidence thresholds
    min_vision_conf: float = 0.6
    min_audio_conf: float = 0.5
    min_temporal_conf: float = 0.6
    
    # Time window (seconds)
    detection_window: float = 10.0
    
    # Minimum duration to trigger (seconds)
    min_duration: float = 3.0


@dataclass
class DetectedEvent:
    """A detected event instance."""
    event_type: EventType
    event_name: str
    confidence: float
    timestamp: float
    duration: float
    
    # Contributing modalities
    vision_confidence: float = 0.0
    audio_confidence: float = 0.0
    temporal_confidence: float = 0.0
    
    # Context
    context: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "event_type": self.event_type.value,
            "event_name": self.event_name,
            "confidence": round(self.confidence, 3),
            "timestamp": self.timestamp,
            "duration": self.duration,
            "modalities": {
                "vision": round(self.vision_confidence, 3),
                "audio": round(self.audio_confidence, 3),
                "temporal": round(self.temporal_confidence, 3)
            },
            "context": self.context
        }


class ModalityAnalyzer:
    """Analyze individual modalities for event cues."""
    
    def __init__(self):
        # Vision cue detectors (simplified - in production use trained models)
        self.vision_cue_weights = {
            "frowning": [0.8, -0.2, 0.1],           # High brow tension, low smile
            "smiling": [-0.3, 0.9, 0.1],            # Low brow, high smile
            "looking_away": [-0.5, 0.0, 0.8],       # Low gaze center, high gaze side
            "eye_rubbing": [0.3, -0.2, 0.7],        # Hand near eye
            "yawning": [0.2, 0.8, -0.1],            # Mouth open wide
            "focused_gaze": [0.1, 0.0, -0.8],       # Steady center gaze
            "confused_look": [0.6, -0.3, 0.2],      # Raised brows, puzzled
        }
        
        # Audio cue detectors
        self.audio_cue_weights = {
            "sighing": [0.7, -0.3, 0.2],            # Long exhale pattern
            "silence": [-0.8, 0.1, 0.0],            # No speech
            "yes_exclamation": [-0.2, 0.9, 0.3],    # Positive exclamation
            "question_tone": [0.4, -0.1, 0.6],      # Rising intonation
            "mumbling": [0.3, -0.4, 0.5],           # Low unclear speech
            "frustrated_sound": [0.8, -0.5, 0.2],   # Negative vocalization
        }
        
        # Temporal/behavioral cue detectors
        self.temporal_cue_weights = {
            "pen_tapping": [0.9, 0.0, 0.1],         # Repetitive hand movement
            "no_movement": [-0.9, -0.1, 0.0],       # Stillness
            "fast_writing": [0.2, 0.8, 0.3],        # Rapid hand motion
            "fidgeting": [0.7, -0.2, 0.4],          # Restless movement
            "stretching": [-0.3, 0.9, 0.2],         # Large body movement
            "leaning_forward": [-0.2, 0.7, 0.3],    # Engaged posture
            "leaning_back": [0.6, -0.4, 0.2],       # Disengaged posture
        }
    
    def analyze_vision(self, vision_features: torch.Tensor) -> Dict[str, float]:
        """Extract vision cues from features."""
        cues = {}
        
        # Simplified: use learned projections
        # In production, use trained classifiers
        for cue_name, weights in self.vision_cue_weights.items():
            # Project features to cue space
            weights_tensor = torch.tensor(weights, dtype=vision_features.dtype, device=vision_features.device)
            
            # Average over sequence
            mean_features = vision_features.mean(dim=1)  # (batch, feature_dim)
            
            # Truncate/pad weights to match feature dim
            if len(weights_tensor) < mean_features.shape[-1]:
                padded_weights = torch.zeros(mean_features.shape[-1], device=vision_features.device)
                padded_weights[:len(weights_tensor)] = weights_tensor
            else:
                padded_weights = weights_tensor[:mean_features.shape[-1]]
            
            # Compute cue score
            score = torch.sigmoid(torch.matmul(mean_features, padded_weights)).item()
            cues[cue_name] = score
        
        return cues
    
    def analyze_audio(self, audio_features: torch.Tensor) -> Dict[str, float]:
        """Extract audio cues from features."""
        cues = {}
        
        for cue_name, weights in self.audio_cue_weights.items():
            weights_tensor = torch.tensor(weights, dtype=audio_features.dtype, device=audio_features.device)
            mean_features = audio_features.mean(dim=1)
            
            if len(weights_tensor) < mean_features.shape[-1]:
                padded_weights = torch.zeros(mean_features.shape[-1], device=audio_features.device)
                padded_weights[:len(weights_tensor)] = weights_tensor
            else:
                padded_weights = weights_tensor[:mean_features.shape[-1]]
            
            score = torch.sigmoid(torch.matmul(mean_features, padded_weights)).item()
            cues[cue_name] = score
        
        return cues
    
    def analyze_temporal(self, temporal_features: torch.Tensor) -> Dict[str, float]:
        """Extract temporal/behavioral cues."""
        cues = {}
        
        for cue_name, weights in self.temporal_cue_weights.items():
            weights_tensor = torch.tensor(weights, dtype=temporal_features.dtype, device=temporal_features.device)
            mean_features = temporal_features.mean(dim=1)
            
            if len(weights_tensor) < mean_features.shape[-1]:
                padded_weights = torch.zeros(mean_features.shape[-1], device=temporal_features.device)
                padded_weights[:len(weights_tensor)] = weights_tensor
            else:
                padded_weights = weights_tensor[:mean_features.shape[-1]]
            
            score = torch.sigmoid(torch.matmul(mean_features, padded_weights)).item()
            cues[cue_name] = score
        
        return cues


class EventDetector:
    """
    Detect complex multimodal events from continuous streams.
    
    Uses temporal sliding windows and pattern matching.
    """
    
    def __init__(self, window_size: int = 30, stride: int = 5):
        self.window_size = window_size  # frames
        self.stride = stride  # frames
        
        self.modality_analyzer = ModalityAnalyzer()
        
        # Event signatures database
        self.event_signatures = self._initialize_signatures()
        
        # Detection history (for temporal patterns)
        self.detection_buffer = deque(maxlen=window_size * 2)
        
        # Active events tracking
        self.active_events: Dict[EventType, Dict] = {}
        
    def _initialize_signatures(self) -> List[EventSignature]:
        """Initialize event signature database."""
        signatures = [
            # Frustration
            EventSignature(
                event_type=EventType.FRUSTRATION,
                name="学习挫败感",
                description="学生表现出沮丧、困惑的情绪",
                vision_cues=["frowning", "confused_look", "looking_away"],
                audio_cues=["sighing", "mumbling", "frustrated_sound"],
                temporal_cues=["pen_tapping", "fidgeting"],
                min_vision_conf=0.5,
                min_audio_conf=0.4,
                min_temporal_conf=0.5,
                detection_window=10.0,
                min_duration=5.0
            ),
            
            # Deep Focus
            EventSignature(
                event_type=EventType.DEEP_FOCUS,
                name="深度专注",
                description="学生处于高度专注状态",
                vision_cues=["focused_gaze"],
                audio_cues=["silence"],
                temporal_cues=["fast_writing"],
                min_vision_conf=0.7,
                min_audio_conf=0.3,
                min_temporal_conf=0.6,
                detection_window=15.0,
                min_duration=10.0
            ),
            
            # Focus Lost
            EventSignature(
                event_type=EventType.FOCUS_LOST,
                name="注意力涣散",
                description="学生注意力从学习转移",
                vision_cues=["looking_away", "yawning"],
                audio_cues=["silence"],
                temporal_cues=["no_movement", "leaning_back"],
                min_vision_conf=0.6,
                min_audio_conf=0.3,
                min_temporal_conf=0.5,
                detection_window=10.0,
                min_duration=5.0
            ),
            
            # Excitement/Breakthrough
            EventSignature(
                event_type=EventType.EXCITEMENT,
                name="突破兴奋",
                description="学生解决问题后的兴奋",
                vision_cues=["smiling"],
                audio_cues=["yes_exclamation"],
                temporal_cues=["fast_writing"],
                min_vision_conf=0.6,
                min_audio_conf=0.7,
                min_temporal_conf=0.5,
                detection_window=5.0,
                min_duration=2.0
            ),
            
            # Fatigue
            EventSignature(
                event_type=EventType.FATIGUE,
                name="疲劳状态",
                description="学生表现出疲劳迹象",
                vision_cues=["eye_rubbing", "yawning"],
                audio_cues=["sighing"],
                temporal_cues=["stretching", "leaning_back"],
                min_vision_conf=0.5,
                min_audio_conf=0.4,
                min_temporal_conf=0.5,
                detection_window=15.0,
                min_duration=8.0
            ),
            
            # Breakthrough
            EventSignature(
                event_type=EventType.BREAKTHROUGH,
                name="学习突破",
                description="学生理解难题的关键时刻",
                vision_cues=["focused_gaze", "smiling"],
                audio_cues=["yes_exclamation", "question_tone"],
                temporal_cues=["leaning_forward", "fast_writing"],
                min_vision_conf=0.5,
                min_audio_conf=0.5,
                min_temporal_conf=0.6,
                detection_window=8.0,
                min_duration=3.0
            ),
            
            # Giving Up
            EventSignature(
                event_type=EventType.GIVING_UP,
                name="放弃倾向",
                description="学生可能准备放弃",
                vision_cues=["looking_away", "frowning"],
                audio_cues=["sighing", "frustrated_sound"],
                temporal_cues=["no_movement", "leaning_back"],
                min_vision_conf=0.6,
                min_audio_conf=0.5,
                min_temporal_conf=0.6,
                detection_window=12.0,
                min_duration=8.0
            ),
        ]
        
        return signatures
    
    def detect_events(
        self,
        features: ModalityFeatures,
        timestamp: Optional[float] = None
    ) -> List[DetectedEvent]:
        """
        Detect events from multimodal features.
        
        Args:
            features: Multimodal features
            timestamp: Current timestamp (default: current time)
            
        Returns:
            List of detected events
        """
        if timestamp is None:
            timestamp = time.time()
        
        detected_events = []
        
        # Analyze each modality
        cues = {}
        
        if features.vision is not None:
            cues['vision'] = self.modality_analyzer.analyze_vision(features.vision)
        
        if features.audio is not None:
            cues['audio'] = self.modality_analyzer.analyze_audio(features.audio)
        
        if features.temporal is not None:
            cues['temporal'] = self.modality_analyzer.analyze_temporal(features.temporal)
        
        # Store in buffer
        self.detection_buffer.append({
            'timestamp': timestamp,
            'cues': cues
        })
        
        # Match against event signatures
        for signature in self.event_signatures:
            event = self._match_signature(signature, cues, timestamp)
            if event:
                detected_events.append(event)
        
        return detected_events
    
    def _match_signature(
        self,
        signature: EventSignature,
        cues: Dict,
        timestamp: float
    ) -> Optional[DetectedEvent]:
        """Match current cues against an event signature."""
        
        # Check if we have required modalities
        has_vision = 'vision' in cues and signature.vision_cues
        has_audio = 'audio' in cues and signature.audio_cues
        has_temporal = 'temporal' in cues and signature.temporal_cues
        
        if not (has_vision or has_audio or has_temporal):
            return None
        
        # Calculate modality confidences
        vision_conf = 0.0
        audio_conf = 0.0
        temporal_conf = 0.0
        
        if has_vision:
            vision_scores = [
                cues['vision'].get(cue, 0.0)
                for cue in signature.vision_cues
            ]
            vision_conf = np.mean(vision_scores) if vision_scores else 0.0
        
        if has_audio:
            audio_scores = [
                cues['audio'].get(cue, 0.0)
                for cue in signature.audio_cues
            ]
            audio_conf = np.mean(audio_scores) if audio_scores else 0.0
        
        if has_temporal:
            temporal_scores = [
                cues['temporal'].get(cue, 0.0)
                for cue in signature.temporal_cues
            ]
            temporal_conf = np.mean(temporal_scores) if temporal_scores else 0.0
        
        # Check thresholds
        if has_vision and vision_conf < signature.min_vision_conf:
            return None
        if has_audio and audio_conf < signature.min_audio_conf:
            return None
        if has_temporal and temporal_conf < signature.min_temporal_conf:
            return None
        
        # Calculate overall confidence (weighted by number of modalities)
        confidences = []
        weights = []
        
        if has_vision:
            confidences.append(vision_conf)
            weights.append(1.0)
        if has_audio:
            confidences.append(audio_conf)
            weights.append(0.8)  # Audio slightly less reliable
        if has_temporal:
            confidences.append(temporal_conf)
            weights.append(1.0)
        
        if not confidences:
            return None
        
        overall_conf = np.average(confidences, weights=weights)
        
        # Only return if confidence is high enough
        if overall_conf < 0.5:
            return None
        
        # Check temporal persistence (event should persist)
        # Simplified: just return if confidence is high
        
        return DetectedEvent(
            event_type=signature.event_type,
            event_name=signature.name,
            confidence=overall_conf,
            timestamp=timestamp,
            duration=signature.min_duration,  # Estimated
            vision_confidence=vision_conf,
            audio_confidence=audio_conf,
            temporal_confidence=temporal_conf,
            context={
                'signature_description': signature.description,
                'matched_cues': {
                    'vision': [c for c in signature.vision_cues if cues.get('vision', {}).get(c, 0) > 0.5],
                    'audio': [c for c in signature.audio_cues if cues.get('audio', {}).get(c, 0) > 0.5],
                    'temporal': [c for c in signature.temporal_cues if cues.get('temporal', {}).get(c, 0) > 0.5]
                }
            }
        )
    
    def get_active_events(self) -> List[DetectedEvent]:
        """Get currently active/persistent events."""
        # Return events that have been detected consistently
        return list(self.active_events.values()) if hasattr(self.active_events, 'values') else []
    
    def reset(self):
        """Reset detector state."""
        self.detection_buffer.clear()
        self.active_events.clear()


class EventActionRecommender:
    """
    Recommend actions based on detected events.
    
    Maps events to appropriate educational interventions.
    """
    
    def __init__(self):
        self.action_map = self._initialize_action_map()
    
    def _initialize_action_map(self) -> Dict[EventType, List[Dict]]:
        """Map events to recommended actions."""
        return {
            EventType.FRUSTRATION: [
                {
                    "action": "offer_help",
                    "message": "这道题看起来有点难呢，需要我帮你理一理思路吗？",
                    "tone": "encouraging",
                    "priority": "high"
                },
                {
                    "action": "take_break",
                    "message": "你已经很努力了，要不要休息5分钟，换个心情再回来？",
                    "tone": "caring",
                    "priority": "medium"
                }
            ],
            
            EventType.FOCUS_LOST: [
                {
                    "action": "gentle_reminder",
                    "message": "嗨，你的思绪好像飘走了，要不要再看看这道题？",
                    "tone": "friendly",
                    "priority": "medium"
                },
                {
                    "action": "change_topic",
                    "message": "要不我们先换个有趣的知识点，然后再回来？",
                    "tone": "engaging",
                    "priority": "low"
                }
            ],
            
            EventType.FATIGUE: [
                {
                    "action": "suggest_rest",
                    "message": "我看到你有点累了，要不要站起来活动一下？做做眼保健操？",
                    "tone": "caring",
                    "priority": "high"
                },
                {
                    "action": "end_session",
                    "message": "今天的学习就到这里吧，你已经很努力了，好好休息！",
                    "tone": "supportive",
                    "priority": "high"
                }
            ],
            
            EventType.BREAKTHROUGH: [
                {
                    "action": "praise",
                    "message": "太棒了！你刚刚的突破真的很厉害，继续保持！",
                    "tone": "excited",
                    "priority": "high"
                },
                {
                    "action": "reinforce",
                    "message": "看，只要坚持就能成功！这种感觉是不是很棒？",
                    "tone": "encouraging",
                    "priority": "medium"
                }
            ],
            
            EventType.DEEP_FOCUS: [
                {
                    "action": "maintain",
                    "message": "",  # Don't interrupt
                    "tone": "silent",
                    "priority": "low"
                }
            ],
            
            EventType.GIVING_UP: [
                {
                    "action": "urgent_support",
                    "message": "等一下！这道题确实很难，但我们可以一步步来，我陪你一起！",
                    "tone": "urgent_caring",
                    "priority": "critical"
                },
                {
                    "action": "simplify",
                    "message": "我们先不看这道题，先从简单的开始，找回信心！",
                    "tone": "supportive",
                    "priority": "high"
                }
            ]
        }
    
    def recommend_actions(self, event: DetectedEvent) -> List[Dict]:
        """
        Recommend actions for a detected event.
        
        Args:
            event: Detected event
            
        Returns:
            List of recommended actions
        """
        actions = self.action_map.get(event.event_type, [])
        
        # Sort by priority and confidence
        prioritized = []
        for action in actions:
            # Adjust priority based on event confidence
            adjusted_priority = action.get("priority", "low")
            if event.confidence > 0.8:
                # High confidence events get higher priority
                priority_map = {"low": "medium", "medium": "high", "high": "critical"}
                adjusted_priority = priority_map.get(adjusted_priority, adjusted_priority)
            
            prioritized.append({
                **action,
                "adjusted_priority": adjusted_priority,
                "event_confidence": event.confidence
            })
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        prioritized.sort(key=lambda x: priority_order.get(x["adjusted_priority"], 4))
        
        return prioritized


# Example usage
def example():
    """Demonstrate event detection."""
    print("=" * 60)
    print("Multimodal Event Detection Example")
    print("=" * 60)
    
    # Create detector
    detector = EventDetector()
    recommender = EventActionRecommender()
    
    # Simulate features for a frustrated student
    features = ModalityFeatures(
        vision=torch.randn(1, 30, 512),    # 30 seconds of video
        audio=torch.randn(1, 30, 128),     # 30 seconds of audio
        temporal=torch.randn(1, 30, 64)    # 30 seconds of behavior
    )
    
    # Add frustration patterns (simulated)
    # Frowning pattern in vision
    features.vision[0, 10:20, 400:450] = 0.8
    # Sighing pattern in audio
    features.audio[0, 15:25, 50:80] = 0.7
    # Pen tapping pattern in temporal
    features.temporal[0, 12:22, 20:40] = 0.9
    
    print("\nSimulating frustrated student scenario...")
    
    # Detect events
    events = detector.detect_events(features)
    
    print(f"\nDetected {len(events)} events:")
    for event in events:
        print(f"\n  Event: {event.event_name}")
        print(f"  Type: {event.event_type.value}")
        print(f"  Confidence: {event.confidence:.2f}")
        print(f"  Vision conf: {event.vision_confidence:.2f}")
        print(f"  Audio conf: {event.audio_confidence:.2f}")
        print(f"  Temporal conf: {event.temporal_confidence:.2f}")
        
        # Get recommendations
        actions = recommender.recommend_actions(event)
        print(f"  Recommended actions:")
        for action in actions[:2]:
            print(f"    - {action['action']}: {action['message'][:50]}...")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    example()
