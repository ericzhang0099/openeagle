"""
API Routes for Multimodal Fusion and Causal Inference

Integrates new modules into FastAPI application.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import numpy as np
import torch

from app.core.fusion import (
    ModalityFeatures,
    EarlyFusion,
    LateFusion,
    AttentionFusion,
    MultimodalClassifier,
    EventDetector,
    EventActionRecommender,
    DetectedEvent,
    EventType,
)
from app.core.causal import (
    CausalGraph,
    CausalDiscovery,
    DoCalculus,
    CounterfactualEngine,
    InterventionOptimizer,
)
from app.core.inference_engine import InferenceEngine, StudentProfile

router = APIRouter(prefix="/api/v1/ai", tags=["advanced-ai"])


# ============================================================================
# Request/Response Models
# ============================================================================

class MultimodalFusionRequest(BaseModel):
    """Request for multimodal fusion."""
    vision_features: Optional[List[List[float]]] = Field(
        None, description="Vision features as list of vectors"
    )
    audio_features: Optional[List[List[float]]] = Field(
        None, description="Audio features as list of vectors"
    )
    text_features: Optional[List[List[float]]] = Field(
        None, description="Text features as list of vectors"
    )
    temporal_features: Optional[List[List[float]]] = Field(
        None, description="Temporal features as list of vectors"
    )
    fusion_type: str = Field("attention", description="early, late, or attention")


class MultimodalFusionResponse(BaseModel):
    """Response from multimodal fusion."""
    fused_features: List[List[float]]
    fusion_type: str
    modalities_used: List[str]


class StudentStateClassificationRequest(BaseModel):
    """Request for student state classification."""
    vision_features: List[List[float]]
    audio_features: Optional[List[List[float]]] = None
    temporal_features: List[List[float]]


class StudentStateClassificationResponse(BaseModel):
    """Response with student state prediction."""
    predicted_state: str
    confidence: float
    all_probabilities: Dict[str, float]


class CausalGraphRequest(BaseModel):
    """Request to build causal graph."""
    variables: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


class CausalDiscoveryRequest(BaseModel):
    """Request for causal discovery from data."""
    data: Dict[str, List[float]]
    method: str = "correlation"
    threshold: float = 0.3


class InterventionRequest(BaseModel):
    """Request for intervention analysis."""
    graph_structure: Dict[str, Any]
    data: Dict[str, List[float]]
    treatment_var: str
    outcome_var: str
    treatment_value: float


class InterventionResponse(BaseModel):
    """Response with intervention effect."""
    expected_outcome: float
    treatment_var: str
    treatment_value: float
    confidence: Optional[float] = None


class CounterfactualRequest(BaseModel):
    """Request for counterfactual analysis."""
    graph_structure: Dict[str, Any]
    data: Dict[str, List[float]]
    observed: Dict[str, float]
    intervention: Dict[str, float]
    target_var: str


class CounterfactualResponse(BaseModel):
    """Response with counterfactual result."""
    counterfactual_value: float
    observed_value: float
    difference: float
    interpretation: str


class OptimizationRequest(BaseModel):
    """Request for intervention optimization."""
    graph_structure: Dict[str, Any]
    data: Dict[str, List[float]]
    treatment_var: str
    outcome_var: str
    outcome_target: float
    treatment_range: List[float]


class OptimizationResponse(BaseModel):
    """Response with optimal intervention."""
    optimal_treatment: float
    expected_outcome: float
    improvement: float


# ============================================================================
# Event Detection & Inference Engine Models
# ============================================================================

class EventDetectionRequest(BaseModel):
    """Request for event detection."""
    vision_features: List[List[float]]
    audio_features: Optional[List[List[float]]] = None
    temporal_features: List[List[float]]


class EventDetectionResponse(BaseModel):
    """Response with detected events."""
    events: List[Dict]
    total_events: int
    highest_confidence_event: Optional[str]


class InferenceRequest(BaseModel):
    """Request for complete inference."""
    student_id: str
    vision_features: List[List[float]]
    audio_features: Optional[List[List[float]]] = None
    temporal_features: List[List[float]]
    context: Optional[Dict] = None


class InferenceResponse(BaseModel):
    """Complete inference response."""
    current_state: str
    state_confidence: float
    events: List[Dict]
    causal_insights: List[Dict]
    immediate_actions: List[Dict]
    long_term_suggestions: List[Dict]
    what_if_scenarios: List[Dict]


class StudentProfileRequest(BaseModel):
    """Request to register student profile."""
    student_id: str
    grade_level: str = "primary_3"
    learning_style: str = "visual"
    average_focus_duration: float = 15.0
    subject_proficiency: Optional[Dict[str, float]] = None


# ============================================================================
# Dependency Injection
# ============================================================================

_fusion_models = {}
_classifier_models = {}
_inference_engine: Optional[InferenceEngine] = None

def get_fusion_model(fusion_type: str = "attention"):
    """Get or create fusion model."""
    if fusion_type not in _fusion_models:
        if fusion_type == "early":
            _fusion_models[fusion_type] = EarlyFusion(output_dim=256)
        elif fusion_type == "late":
            _fusion_models[fusion_type] = LateFusion(output_dim=256)
        elif fusion_type == "attention":
            _fusion_models[fusion_type] = AttentionFusion(
                hidden_dim=256,
                num_heads=8,
                num_layers=2
            )
        else:
            raise ValueError(f"Unknown fusion type: {fusion_type}")
    return _fusion_models[fusion_type]


def get_classifier_model():
    """Get or create classifier model."""
    if "student_state" not in _classifier_models:
        _classifier_models["student_state"] = MultimodalClassifier(
            fusion_type="attention",
            num_classes=5,
            hidden_dim=256,
            num_heads=8,
            num_layers=2
        )
    return _classifier_models["student_state"]


def get_inference_engine() -> InferenceEngine:
    """Get or create inference engine."""
    global _inference_engine
    if _inference_engine is None:
        _inference_engine = InferenceEngine()
    return _inference_engine


# ============================================================================
# API Endpoints - Multimodal Fusion
# ============================================================================

@router.post("/fusion", response_model=MultimodalFusionResponse)
async def fuse_modalities(request: MultimodalFusionRequest):
    """Fuse features from multiple modalities."""
    try:
        features = ModalityFeatures()
        modalities_used = []
        
        if request.vision_features:
            features.vision = torch.tensor(request.vision_features).float()
            modalities_used.append("vision")
        
        if request.audio_features:
            features.audio = torch.tensor(request.audio_features).float()
            modalities_used.append("audio")
        
        if request.text_features:
            features.text = torch.tensor(request.text_features).float()
            modalities_used.append("text")
        
        if request.temporal_features:
            features.temporal = torch.tensor(request.temporal_features).float()
            modalities_used.append("temporal")
        
        if not modalities_used:
            raise HTTPException(status_code=400, detail="No features provided")
        
        fusion_model = get_fusion_model(request.fusion_type)
        
        with torch.no_grad():
            fused = fusion_model(features)
        
        if request.fusion_type == "attention":
            fused_list = fused.numpy().tolist()
        else:
            fused_list = fused.numpy().tolist()
        
        return MultimodalFusionResponse(
            fused_features=fused_list,
            fusion_type=request.fusion_type,
            modalities_used=modalities_used
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/student-state", response_model=StudentStateClassificationResponse)
async def classify_student_state(request: StudentStateClassificationRequest):
    """Classify student state from multimodal data."""
    try:
        features = ModalityFeatures(
            vision=torch.tensor(request.vision_features).float(),
            temporal=torch.tensor(request.temporal_features).float()
        )
        
        if request.audio_features:
            features.audio = torch.tensor(request.audio_features).float()
        
        classifier = get_classifier_model()
        
        with torch.no_grad():
            logits = classifier(features)
            probs = torch.softmax(logits, dim=-1)
        
        pred_idx = probs.argmax(dim=-1).item()
        confidence = probs.max(dim=-1).values.item()
        
        state_names = ["focused", "distracted", "tired", "excited", "confused"]
        predicted_state = state_names[pred_idx]
        
        all_probs = {
            state_names[i]: probs[0, i].item()
            for i in range(len(state_names))
        }
        
        return StudentStateClassificationResponse(
            predicted_state=predicted_state,
            confidence=confidence,
            all_probabilities=all_probs
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# API Endpoints - Causal Inference
# ============================================================================

@router.post("/causal/discover", response_model=Dict[str, Any])
async def discover_causal_relationships(request: CausalDiscoveryRequest):
    """Discover causal relationships from observational data."""
    try:
        data = {k: np.array(v) for k, v in request.data.items()}
        
        discovery = CausalDiscovery(method=request.method)
        
        if request.method == "correlation":
            graph = discovery.correlation_based(data, threshold=request.threshold)
        elif request.method == "granger":
            graph = discovery.granger_causality(data)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown method: {request.method}")
        
        edges = [
            {
                "source": e.source,
                "target": e.target,
                "strength": e.strength,
                "confidence": e.confidence
            }
            for e in graph.edges.values()
        ]
        
        return {
            "variables": list(graph.variables.keys()),
            "edges": edges,
            "method": request.method
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/causal/intervention", response_model=InterventionResponse)
async def compute_intervention_effect(request: InterventionRequest):
    """Compute the effect of an intervention using do-calculus."""
    try:
        graph = CausalGraph()
        for var in request.graph_structure.get("variables", []):
            graph.add_variable(var["name"], var.get("type", "continuous"))
        
        for edge in request.graph_structure.get("edges", []):
            graph.add_edge(edge["source"], edge["target"], strength=edge.get("strength", 0.0))
        
        data = {k: np.array(v) for k, v in request.data.items()}
        
        do_calc = DoCalculus(graph)
        effect = do_calc.compute_intervention(
            data, request.treatment_var, request.outcome_var, request.treatment_value
        )
        
        if np.isnan(effect):
            raise HTTPException(status_code=400, detail="Could not compute intervention effect")
        
        return InterventionResponse(
            expected_outcome=float(effect),
            treatment_var=request.treatment_var,
            treatment_value=request.treatment_value
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/causal/counterfactual", response_model=CounterfactualResponse)
async def compute_counterfactual(request: CounterfactualRequest):
    """Compute counterfactual: What would have happened if...?"""
    try:
        graph = CausalGraph()
        for var in request.graph_structure.get("variables", []):
            graph.add_variable(var["name"], var.get("type", "continuous"))
        
        for edge in request.graph_structure.get("edges", []):
            graph.add_edge(edge["source"], edge["target"])
        
        data = {k: np.array(v) for k, v in request.data.items()}
        
        cf_engine = CounterfactualEngine(graph)
        counterfactual = cf_engine.compute_counterfactual(
            data, request.observed, request.intervention, request.target_var
        )
        
        observed_value = request.observed.get(request.target_var, 0)
        difference = counterfactual - observed_value
        
        if difference > 0:
            interpretation = f"If the intervention had occurred, {request.target_var} would have been {difference:.2f} points higher."
        elif difference < 0:
            interpretation = f"If the intervention had occurred, {request.target_var} would have been {abs(difference):.2f} points lower."
        else:
            interpretation = "The intervention would not have changed the outcome."
        
        return CounterfactualResponse(
            counterfactual_value=float(counterfactual),
            observed_value=float(observed_value),
            difference=float(difference),
            interpretation=interpretation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/causal/optimize", response_model=OptimizationResponse)
async def optimize_intervention(request: OptimizationRequest):
    """Find the optimal intervention to achieve a desired outcome."""
    try:
        graph = CausalGraph()
        for var in request.graph_structure.get("variables", []):
            graph.add_variable(var["name"], var.get("type", "continuous"))
        
        for edge in request.graph_structure.get("edges", []):
            graph.add_edge(edge["source"], edge["target"])
        
        data = {k: np.array(v) for k, v in request.data.items()}
        
        optimizer = InterventionOptimizer(graph)
        result = optimizer.find_optimal_intervention(
            data,
            request.treatment_var,
            request.outcome_var,
            request.outcome_target,
            (request.treatment_range[0], request.treatment_range[1]),
            step=0.5
        )
        
        current_mean = np.mean(data.get(request.outcome_var, [0]))
        improvement = result["actual_expected"] - current_mean if result["actual_expected"] else 0
        
        return OptimizationResponse(
            optimal_treatment=result["optimal_treatment"],
            expected_outcome=result["actual_expected"] or 0,
            improvement=float(improvement)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# API Endpoints - Event Detection & Inference Engine
# ============================================================================

@router.post("/events/detect", response_model=EventDetectionResponse)
async def detect_events(request: EventDetectionRequest):
    """
    Detect complex multimodal events (frustration, breakthrough, fatigue, etc.).
    
    Analyzes vision, audio, and temporal patterns to identify student events.
    """
    try:
        features = ModalityFeatures(
            vision=torch.tensor(request.vision_features).float(),
            temporal=torch.tensor(request.temporal_features).float()
        )
        
        if request.audio_features:
            features.audio = torch.tensor(request.audio_features).float()
        
        detector = EventDetector()
        events = detector.detect_events(features)
        
        event_dicts = [e.to_dict() for e in events]
        
        highest_conf = None
        if events:
            highest = max(events, key=lambda e: e.confidence)
            highest_conf = f"{highest.event_name} ({highest.confidence:.2f})"
        
        return EventDetectionResponse(
            events=event_dicts,
            total_events=len(events),
            highest_confidence_event=highest_conf
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inference/complete", response_model=InferenceResponse)
async def complete_inference(request: InferenceRequest):
    """
    Run complete inference pipeline.
    
    Combines state classification, event detection, causal analysis,
    and personalized recommendations.
    """
    try:
        engine = get_inference_engine()
        
        features = ModalityFeatures(
            vision=torch.tensor(request.vision_features).float(),
            temporal=torch.tensor(request.temporal_features).float()
        )
        
        if request.audio_features:
            features.audio = torch.tensor(request.audio_features).float()
        
        result = engine.infer(
            student_id=request.student_id,
            features=features,
            context=request.context
        )
        
        return InferenceResponse(
            current_state=result.current_state,
            state_confidence=result.state_confidence,
            events=[e.to_dict() for e in result.events],
            causal_insights=result.causal_insights,
            immediate_actions=result.immediate_actions,
            long_term_suggestions=result.long_term_suggestions,
            what_if_scenarios=result.what_if_scenarios
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/students/register")
async def register_student(request: StudentProfileRequest):
    """Register a student profile for personalized inference."""
    try:
        engine = get_inference_engine()
        
        profile = StudentProfile(
            student_id=request.student_id,
            grade_level=request.grade_level,
            learning_style=request.learning_style,
            average_focus_duration=request.average_focus_duration,
            subject_proficiency=request.subject_proficiency or {}
        )
        
        engine.register_student(profile)
        
        return {
            "code": 0,
            "message": "Student registered successfully",
            "data": {"student_id": request.student_id}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students/{student_id}/summary")
async def get_student_summary(student_id: str):
    """Get learning summary for a student."""
    try:
        engine = get_inference_engine()
        summary = engine.get_student_summary(student_id)
        
        return {
            "code": 0,
            "message": "success",
            "data": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
