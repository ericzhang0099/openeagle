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
)
from app.core.causal import (
    CausalGraph,
    CausalDiscovery,
    DoCalculus,
    CounterfactualEngine,
    InterventionOptimizer,
)

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
# Dependency Injection
# ============================================================================

_fusion_models = {}
_classifier_models = {}

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
            num_classes=5,  # focused, distracted, tired, excited, confused
            hidden_dim=256,
            num_heads=8,
            num_layers=2
        )
    return _classifier_models["student_state"]


# ============================================================================
# API Endpoints - Multimodal Fusion
# ============================================================================

@router.post("/fusion", response_model=MultimodalFusionResponse)
async def fuse_modalities(request: MultimodalFusionRequest):
    """
    Fuse features from multiple modalities.
    
    Supports early, late, and attention-based fusion strategies.
    """
    try:
        # Convert lists to tensors
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
        
        # Get fusion model
        fusion_model = get_fusion_model(request.fusion_type)
        
        # Run fusion
        with torch.no_grad():
            fused = fusion_model(features)
        
        # Convert back to list
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
    """
    Classify student state (focused, distracted, tired, etc.) from multimodal data.
    
    This is the main endpoint for VisionClaw's student monitoring feature.
    """
    try:
        # Build features
        features = ModalityFeatures(
            vision=torch.tensor(request.vision_features).float(),
            temporal=torch.tensor(request.temporal_features).float()
        )
        
        if request.audio_features:
            features.audio = torch.tensor(request.audio_features).float()
        
        # Get classifier
        classifier = get_classifier_model()
        
        # Classify
        with torch.no_grad():
            logits = classifier(features)
            probs = torch.softmax(logits, dim=-1)
        
        # Get prediction
        pred_idx = probs.argmax(dim=-1).item()
        confidence = probs.max(dim=-1).values.item()
        
        state_names = ["focused", "distracted", "tired", "excited", "confused"]
        predicted_state = state_names[pred_idx]
        
        # All probabilities
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
    """
    Discover causal relationships from observational data.
    
    Uses correlation-based or Granger causality methods.
    """
    try:
        # Convert data to numpy
        data = {
            k: np.array(v)
            for k, v in request.data.items()
        }
        
        # Run discovery
        discovery = CausalDiscovery(method=request.method)
        
        if request.method == "correlation":
            graph = discovery.correlation_based(data, threshold=request.threshold)
        elif request.method == "granger":
            graph = discovery.granger_causality(data)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown method: {request.method}")
        
        # Format response
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
    """
    Compute the effect of an intervention using do-calculus.
    
    Example: "What is the expected learning score if we ensure 8 hours of sleep?"
    """
    try:
        # Build graph from structure
        graph = CausalGraph()
        for var in request.graph_structure.get("variables", []):
            graph.add_variable(var["name"], var.get("type", "continuous"))
        
        for edge in request.graph_structure.get("edges", []):
            graph.add_edge(
                edge["source"],
                edge["target"],
                strength=edge.get("strength", 0.0)
            )
        
        # Convert data
        data = {
            k: np.array(v)
            for k, v in request.data.items()
        }
        
        # Compute intervention
        do_calc = DoCalculus(graph)
        effect = do_calc.compute_intervention(
            data,
            request.treatment_var,
            request.outcome_var,
            request.treatment_value
        )
        
        if np.isnan(effect):
            raise HTTPException(
                status_code=400,
                detail="Could not compute intervention effect. Check data and graph structure."
            )
        
        return InterventionResponse(
            expected_outcome=float(effect),
            treatment_var=request.treatment_var,
            treatment_value=request.treatment_value
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/causal/counterfactual", response_model=CounterfactualResponse)
async def compute_counterfactual(request: CounterfactualRequest):
    """
    Compute counterfactual: "What would have happened if...?"
    
    Example: "What would the test score be if the child had slept 8 hours instead of 6?"
    """
    try:
        # Build graph
        graph = CausalGraph()
        for var in request.graph_structure.get("variables", []):
            graph.add_variable(var["name"], var.get("type", "continuous"))
        
        for edge in request.graph_structure.get("edges", []):
            graph.add_edge(edge["source"], edge["target"])
        
        # Convert data
        data = {
            k: np.array(v)
            for k, v in request.data.items()
        }
        
        # Compute counterfactual
        cf_engine = CounterfactualEngine(graph)
        counterfactual = cf_engine.compute_counterfactual(
            data,
            request.observed,
            request.intervention,
            request.target_var
        )
        
        observed_value = request.observed.get(request.target_var, 0)
        difference = counterfactual - observed_value
        
        # Generate interpretation
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
    """
    Find the optimal intervention to achieve a desired outcome.
    
    Example: "How many hours of sleep are needed to achieve a test score of 85?"
    """
    try:
        # Build graph
        graph = CausalGraph()
        for var in request.graph_structure.get("variables", []):
            graph.add_variable(var["name"], var.get("type", "continuous"))
        
        for edge in request.graph_structure.get("edges", []):
            graph.add_edge(edge["source"], edge["target"])
        
        # Convert data
        data = {
            k: np.array(v)
            for k, v in request.data.items()
        }
        
        # Optimize
        optimizer = InterventionOptimizer(graph)
        result = optimizer.find_optimal_intervention(
            data,
            request.treatment_var,
            request.outcome_var,
            request.outcome_target,
            (request.treatment_range[0], request.treatment_range[1]),
            step=0.5
        )
        
        # Calculate improvement
        current_mean = np.mean(data.get(request.outcome_var, [0]))
        improvement = result["actual_expected"] - current_mean if result["actual_expected"] else 0
        
        return OptimizationResponse(
            optimal_treatment=result["optimal_treatment"],
            expected_outcome=result["actual_expected"] or 0,
            improvement=float(improvement)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
