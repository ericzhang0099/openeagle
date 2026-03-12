"""
Inference Engine for Student Behavior Analysis

Provides high-level inference capabilities combining:
- Multimodal fusion
- Causal inference  
- Event detection
- Personalized recommendations

This is the "brain" that ties together all AI components.
"""

import torch
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
import time

from app.core.fusion import (
    ModalityFeatures, 
    AttentionFusion,
    MultimodalClassifier
)
from app.core.fusion.event_detection import (
    EventDetector,
    EventActionRecommender,
    DetectedEvent,
    EventType
)
from app.core.causal import (
    CausalGraph,
    DoCalculus,
    CounterfactualEngine,
    InterventionOptimizer
)
from app.utils.logger import logger


@dataclass
class StudentProfile:
    """Student learning profile for personalization."""
    student_id: str
    grade_level: str = "primary_3"  # e.g., primary_1, middle_2
    learning_style: str = "visual"  # visual, auditory, kinesthetic
    
    # Historical data
    average_focus_duration: float = 15.0  # minutes
    best_learning_time: str = "morning"  # morning, afternoon, evening
    
    # Subject strengths/weaknesses
    subject_proficiency: Dict[str, float] = None  # e.g., {"math": 0.8, "english": 0.6}
    
    # Behavioral patterns
    common_frustration_triggers: List[str] = None
    effective_motivations: List[str] = None
    
    # Parent/AE preferences
    parent_priorities: List[str] = None  # e.g., ["habits", "grades", "interest"]
    
    def __post_init__(self):
        if self.subject_proficiency is None:
            self.subject_proficiency = {}
        if self.common_frustration_triggers is None:
            self.common_frustration_triggers = []
        if self.effective_motivations is None:
            self.effective_motivations = []
        if self.parent_priorities is None:
            self.parent_priorities = ["balanced"]


@dataclass
class InferenceResult:
    """Result from inference engine."""
    timestamp: float
    
    # State detection
    current_state: str
    state_confidence: float
    
    # Events detected
    events: List[DetectedEvent]
    
    # Causal analysis
    causal_insights: List[Dict]
    
    # Recommendations
    immediate_actions: List[Dict]
    long_term_suggestions: List[Dict]
    
    # Counterfactuals
    what_if_scenarios: List[Dict]
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "current_state": self.current_state,
            "state_confidence": round(self.state_confidence, 3),
            "events": [e.to_dict() for e in self.events],
            "causal_insights": self.causal_insights,
            "immediate_actions": self.immediate_actions,
            "long_term_suggestions": self.long_term_suggestions,
            "what_if_scenarios": self.what_if_scenarios
        }


class InferenceEngine:
    """
    Central inference engine for VisionClaw.
    
    Combines multiple AI capabilities:
    1. Multimodal state classification
    2. Event detection
    3. Causal analysis
    4. Personalized recommendations
    """
    
    def __init__(self):
        # Core components
        self.fusion_model = AttentionFusion(
            vision_dim=512,
            audio_dim=128,
            temporal_dim=64,
            hidden_dim=256,
            num_heads=8,
            num_layers=2
        )
        
        self.state_classifier = MultimodalClassifier(
            fusion_type="attention",
            num_classes=5,
            hidden_dim=256
        )
        
        self.event_detector = EventDetector()
        self.action_recommender = EventActionRecommender()
        
        # Student profiles cache
        self.student_profiles: Dict[str, StudentProfile] = {}
        
        # Historical data for causal analysis
        self.observation_history: Dict[str, List[Dict]] = defaultdict(list)
        
        # Causal models per student (learned over time)
        self.student_causal_models: Dict[str, CausalGraph] = {}
        
        logger.info("InferenceEngine initialized")
    
    def register_student(self, profile: StudentProfile):
        """Register a student profile."""
        self.student_profiles[profile.student_id] = profile
        logger.info(f"Registered student: {profile.student_id}")
    
    def infer(
        self,
        student_id: str,
        features: ModalityFeatures,
        context: Optional[Dict] = None
    ) -> InferenceResult:
        """
        Run complete inference pipeline.
        
        Args:
            student_id: Student identifier
            features: Multimodal features
            context: Additional context (subject, task difficulty, etc.)
            
        Returns:
            Complete inference result
        """
        timestamp = time.time()
        context = context or {}
        
        # Get student profile
        profile = self.student_profiles.get(student_id)
        if not profile:
            profile = StudentProfile(student_id=student_id)
            self.register_student(profile)
        
        # Step 1: Classify current state
        state, state_conf = self._classify_state(features)
        
        # Step 2: Detect events
        events = self.event_detector.detect_events(features, timestamp)
        
        # Step 3: Store observation
        observation = {
            'timestamp': timestamp,
            'state': state,
            'events': [e.event_type.value for e in events],
            'context': context
        }
        self.observation_history[student_id].append(observation)
        
        # Step 4: Causal analysis
        causal_insights = self._analyze_causality(student_id, events, context)
        
        # Step 5: Generate recommendations
        immediate_actions = self._generate_immediate_actions(
            events, profile, context
        )
        
        long_term_suggestions = self._generate_long_term_suggestions(
            student_id, profile, context
        )
        
        # Step 6: Counterfactual scenarios
        what_if_scenarios = self._generate_what_if_scenarios(
            student_id, events, profile
        )
        
        return InferenceResult(
            timestamp=timestamp,
            current_state=state,
            state_confidence=state_conf,
            events=events,
            causal_insights=causal_insights,
            immediate_actions=immediate_actions,
            long_term_suggestions=long_term_suggestions,
            what_if_scenarios=what_if_scenarios
        )
    
    def _classify_state(
        self,
        features: ModalityFeatures
    ) -> Tuple[str, float]:
        """Classify student's current state."""
        with torch.no_grad():
            logits = self.state_classifier(features)
            probs = torch.softmax(logits, dim=-1)
            
            pred_idx = probs.argmax(dim=-1).item()
            confidence = probs.max(dim=-1).values.item()
        
        state_names = ["focused", "distracted", "tired", "excited", "confused"]
        return state_names[pred_idx], confidence
    
    def _analyze_causality(
        self,
        student_id: str,
        events: List[DetectedEvent],
        context: Dict
    ) -> List[Dict]:
        """Generate causal insights."""
        insights = []
        
        history = self.observation_history[student_id]
        if len(history) < 10:
            return insights  # Not enough data
        
        # Simple pattern: Check if sleep correlates with focus
        # In production, use proper causal discovery
        
        # Check for recurring patterns
        recent_events = [e.event_type for e in events]
        
        if EventType.FRUSTRATION in recent_events:
            # Check if frustration often leads to giving up
            frustration_count = sum(
                1 for obs in history[-50:]
                if 'frustration' in obs.get('events', [])
            )
            
            if frustration_count > 5:
                insights.append({
                    "type": "pattern",
                    "finding": f"Student shows frustration {frustration_count} times in recent sessions",
                    "recommendation": "Consider adjusting difficulty or providing more scaffolding",
                    "confidence": min(frustration_count / 10, 0.9)
                })
        
        if EventType.DEEP_FOCUS in recent_events:
            insights.append({
                "type": "positive",
                "finding": "Student entered deep focus state",
                "recommendation": "Maintain current approach, this is working well",
                "confidence": 0.8
            })
        
        return insights
    
    def _generate_immediate_actions(
        self,
        events: List[DetectedEvent],
        profile: StudentProfile,
        context: Dict
    ) -> List[Dict]:
        """Generate immediate action recommendations."""
        actions = []
        
        for event in events:
            recommended = self.action_recommender.recommend_actions(event)
            
            for action in recommended:
                # Personalize based on profile
                personalized_action = self._personalize_action(action, profile, event)
                actions.append(personalized_action)
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        actions.sort(key=lambda x: priority_order.get(x.get("priority"), 4))
        
        return actions[:3]  # Return top 3
    
    def _personalize_action(
        self,
        action: Dict,
        profile: StudentProfile,
        event: DetectedEvent
    ) -> Dict:
        """Personalize action based on student profile."""
        personalized = action.copy()
        
        # Adjust message based on learning style
        if profile.learning_style == "visual" and "visual" not in personalized.get("message", "").lower():
            personalized["message"] = personalized.get("message", "") + " 我可以画个图帮你理解。"
        
        elif profile.learning_style == "auditory" and event.event_type == EventType.FRUSTRATION:
            personalized["message"] = personalized.get("message", "").replace("看", "听")
        
        # Adjust based on grade level
        if profile.grade_level.startswith("primary"):
            # Simpler language for younger students
            personalized["message"] = personalized.get("message", "").replace("理一理思路", "一起想一想")
        
        return personalized
    
    def _generate_long_term_suggestions(
        self,
        student_id: str,
        profile: StudentProfile,
        context: Dict
    ) -> List[Dict]:
        """Generate long-term learning suggestions."""
        suggestions = []
        
        history = self.observation_history[student_id]
        
        # Analyze focus patterns
        focus_times = [
            obs['timestamp'] for obs in history
            if obs.get('state') == 'focused'
        ]
        
        if focus_times and len(focus_times) > 5:
            # Calculate average focus session length
            focus_durations = []
            for i in range(1, len(focus_times)):
                duration = (focus_times[i] - focus_times[i-1]) / 60  # minutes
                if duration < 60:  # Ignore gaps > 1 hour
                    focus_durations.append(duration)
            
            if focus_durations:
                avg_focus = np.mean(focus_durations)
                
                if avg_focus < profile.average_focus_duration * 0.7:
                    suggestions.append({
                        "type": "habit",
                        "suggestion": "建议采用番茄工作法，每15分钟休息一次",
                        "reason": f"最近平均专注时间({avg_focus:.0f}分钟)低于平时水平",
                        "priority": "high"
                    })
                elif avg_focus > profile.average_focus_duration * 1.3:
                    suggestions.append({
                        "type": "habit",
                        "suggestion": "可以适当延长单次学习时间",
                        "reason": f"最近专注时间({avg_focus:.0f}分钟)有提升",
                        "priority": "medium"
                    })
        
        # Subject-specific suggestions
        current_subject = context.get('subject', '')
        if current_subject and current_subject in profile.subject_proficiency:
            proficiency = profile.subject_proficiency[current_subject]
            if proficiency < 0.5:
                suggestions.append({
                    "type": "subject",
                    "suggestion": f"建议加强{current_subject}的基础练习",
                    "reason": f"该科目掌握程度({proficiency:.0%})需要提升",
                    "priority": "high"
                })
        
        return suggestions
    
    def _generate_what_if_scenarios(
        self,
        student_id: str,
        events: List[DetectedEvent],
        profile: StudentProfile
    ) -> List[Dict]:
        """Generate "what if" counterfactual scenarios."""
        scenarios = []
        
        # Scenario 1: What if we had intervened earlier?
        frustration_events = [e for e in events if e.event_type == EventType.FRUSTRATION]
        if frustration_events:
            scenarios.append({
                "scenario": "如果早点发现困惑并提供帮助",
                "current_outcome": "学生经历挫折",
                "hypothetical_outcome": "可能顺利解决问题，保持学习动力",
                "action": "下次注意早期信号，提前介入",
                "applicability": "high" if len(frustration_events) > 1 else "medium"
            })
        
        # Scenario 2: What if we adjust difficulty?
        if profile.subject_proficiency:
            avg_proficiency = np.mean(list(profile.subject_proficiency.values()))
            if avg_proficiency < 0.6:
                scenarios.append({
                    "scenario": "如果降低学习难度",
                    "current_outcome": "持续挫败，可能失去兴趣",
                    "hypothetical_outcome": "建立信心，逐步提升",
                    "action": "调整至适合当前水平的内容",
                    "applicability": "high"
                })
        
        return scenarios
    
    def predict_optimal_intervention(
        self,
        student_id: str,
        target_outcome: str,
        current_context: Dict
    ) -> Dict:
        """
        Predict the optimal intervention for desired outcome.
        
        Uses causal inference to recommend best action.
        """
        # This would use the full causal inference pipeline
        # Simplified version for now
        
        profile = self.student_profiles.get(student_id)
        
        recommendations = {
            "improve_focus": {
                "intervention": "减少环境干扰 + 短时间专注训练",
                "expected_improvement": "20-30%",
                "confidence": 0.7
            },
            "reduce_frustration": {
                "intervention": "降低难度 + 增加正向反馈",
                "expected_improvement": "40-50%",
                "confidence": 0.8
            },
            "increase_engagement": {
                "intervention": "结合兴趣点 + 游戏化元素",
                "expected_improvement": "30-40%",
                "confidence": 0.75
            }
        }
        
        return recommendations.get(target_outcome, {
            "intervention": "需要更多数据分析",
            "expected_improvement": "unknown",
            "confidence": 0.0
        })
    
    def get_student_summary(self, student_id: str) -> Dict:
        """Get learning summary for a student."""
        history = self.observation_history.get(student_id, [])
        profile = self.student_profiles.get(student_id)
        
        if not history:
            return {"error": "No data available"}
        
        # Calculate statistics
        states = [obs.get('state') for obs in history]
        state_counts = defaultdict(int)
        for s in states:
            state_counts[s] += 1
        
        total_sessions = len(history)
        
        return {
            "student_id": student_id,
            "total_observations": total_sessions,
            "state_distribution": dict(state_counts),
            "focus_rate": state_counts.get('focused', 0) / total_sessions if total_sessions > 0 else 0,
            "profile": {
                "grade": profile.grade_level if profile else "unknown",
                "learning_style": profile.learning_style if profile else "unknown"
            },
            "recent_events": [
                obs.get('events', []) for obs in history[-5:]
            ]
        }


# Example usage
def example():
    """Demonstrate inference engine."""
    print("=" * 60)
    print("Inference Engine Example")
    print("=" * 60)
    
    # Create engine
    engine = InferenceEngine()
    
    # Register student
    profile = StudentProfile(
        student_id="student_001",
        grade_level="primary_3",
        learning_style="visual",
        average_focus_duration=20.0,
        subject_proficiency={"math": 0.7, "english": 0.5}
    )
    engine.register_student(profile)
    
    # Simulate observation
    features = ModalityFeatures(
        vision=torch.randn(1, 30, 512),
        audio=torch.randn(1, 30, 128),
        temporal=torch.randn(1, 30, 64)
    )
    
    # Add frustration pattern
    features.vision[0, 10:25, 400:450] = 0.8  # Frowning
    features.audio[0, 15:28, 50:80] = 0.6     # Sighing
    
    print("\nRunning inference...")
    
    # Run inference
    result = engine.infer(
        student_id="student_001",
        features=features,
        context={"subject": "math", "difficulty": "hard"}
    )
    
    print("\n" + "=" * 60)
    print("Inference Result:")
    print("=" * 60)
    
    print(f"\nCurrent State: {result.current_state} (confidence: {result.state_confidence:.2f})")
    
    print(f"\nDetected Events ({len(result.events)}):")
    for event in result.events:
        print(f"  - {event.event_name}: {event.confidence:.2f}")
    
    print(f"\nImmediate Actions ({len(result.immediate_actions)}):")
    for action in result.immediate_actions[:2]:
        print(f"  - {action.get('action')}: {action.get('message', '')[:40]}...")
    
    print(f"\nCausal Insights ({len(result.causal_insights)}):")
    for insight in result.causal_insights:
        print(f"  - {insight.get('finding')}")
    
    # Get student summary
    summary = engine.get_student_summary("student_001")
    print(f"\nStudent Summary:")
    print(f"  Total observations: {summary['total_observations']}")
    print(f"  Focus rate: {summary['focus_rate']:.1%}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    example()
