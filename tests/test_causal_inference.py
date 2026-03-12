"""
Unit Tests for Causal Inference System

Tests cover:
- Causal graph construction
- Path finding
- Do-calculus computations
- Counterfactual reasoning
- Intervention optimization
"""

import pytest
import numpy as np
from app.core.causal import (
    CausalVariable,
    CausalEdge,
    CausalGraph,
    CausalDiscovery,
    DoCalculus,
    CounterfactualEngine,
    InterventionOptimizer,
)


class TestCausalGraph:
    """Test CausalGraph construction and queries."""
    
    @pytest.fixture
    def simple_graph(self):
        """Create a simple causal graph: X -> Y -> Z"""
        graph = CausalGraph()
        graph.add_variable("X", "continuous")
        graph.add_variable("Y", "continuous")
        graph.add_variable("Z", "continuous")
        graph.add_edge("X", "Y", strength=0.7)
        graph.add_edge("Y", "Z", strength=0.8)
        return graph
    
    def test_add_variable(self):
        """Test adding variables."""
        graph = CausalGraph()
        var = graph.add_variable("test_var", "continuous")
        
        assert "test_var" in graph.variables
        assert var.name == "test_var"
        assert var.var_type == "continuous"
    
    def test_add_edge(self, simple_graph):
        """Test adding edges."""
        assert len(simple_graph.edges) == 2
        assert ("X", "Y") in simple_graph.edges
        assert ("Y", "Z") in simple_graph.edges
        
        edge = simple_graph.edges[("X", "Y")]
        assert edge.strength == 0.7
        assert edge.source == "X"
        assert edge.target == "Y"
    
    def test_get_parents(self, simple_graph):
        """Test parent query."""
        assert simple_graph.get_parents("Y") == ["X"]
        assert simple_graph.get_parents("Z") == ["Y"]
        assert simple_graph.get_parents("X") == []
    
    def test_get_children(self, simple_graph):
        """Test children query."""
        assert simple_graph.get_children("X") == ["Y"]
        assert simple_graph.get_children("Y") == ["Z"]
        assert simple_graph.get_children("Z") == []
    
    def test_get_ancestors(self, simple_graph):
        """Test ancestor query."""
        assert simple_graph.get_ancestors("X") == set()
        assert simple_graph.get_ancestors("Y") == {"X"}
        assert simple_graph.get_ancestors("Z") == {"X", "Y"}
    
    def test_find_paths(self, simple_graph):
        """Test path finding."""
        paths = simple_graph.find_paths("X", "Z")
        assert len(paths) == 1
        assert paths[0] == ["X", "Y", "Z"]
    
    def test_is_valid_dag(self, simple_graph):
        """Test DAG validation."""
        assert simple_graph.is_valid()
    
    def test_invalid_cycle(self):
        """Test that cycles are detected."""
        graph = CausalGraph()
        graph.add_variable("A")
        graph.add_variable("B")
        graph.add_edge("A", "B")
        
        # This creates a cycle
        graph.graph.add_edge("B", "A")  # Bypass add_edge to force cycle
        
        assert not graph.is_valid()


class TestCausalDiscovery:
    """Test causal discovery from data."""
    
    def test_correlation_based_discovery(self):
        """Test simple correlation-based discovery."""
        np.random.seed(42)
        n = 100
        
        # X causes Y
        X = np.random.normal(0, 1, n)
        Y = 0.8 * X + np.random.normal(0, 0.3, n)
        
        data = {"X": X, "Y": Y}
        
        discovery = CausalDiscovery()
        graph = discovery.correlation_based(data, threshold=0.5)
        
        # Should discover relationship
        assert len(graph.edges) >= 1
    
    def test_no_correlation(self):
        """Test with uncorrelated variables."""
        np.random.seed(42)
        n = 100
        
        X = np.random.normal(0, 1, n)
        Y = np.random.normal(0, 1, n)  # Independent
        
        data = {"X": X, "Y": Y}
        
        discovery = CausalDiscovery()
        graph = discovery.correlation_based(data, threshold=0.3)
        
        # Should not discover spurious relationship
        assert len(graph.edges) == 0


class TestDoCalculus:
    """Test do-calculus intervention computations."""
    
    @pytest.fixture
    def simple_graph(self):
        """Graph: X -> Y"""
        graph = CausalGraph()
        graph.add_variable("X")
        graph.add_variable("Y")
        graph.add_edge("X", "Y", strength=0.6)
        return graph
    
    @pytest.fixture
    def confounded_graph(self):
        """Graph: Z -> X -> Y, Z -> Y (confounding)"""
        graph = CausalGraph()
        graph.add_variable("Z")
        graph.add_variable("X")
        graph.add_variable("Y")
        graph.add_edge("Z", "X", strength=0.5)
        graph.add_edge("X", "Y", strength=0.6)
        graph.add_edge("Z", "Y", strength=0.4)
        return graph
    
    def test_identify_confounders(self, confounded_graph):
        """Test confounder identification."""
        do_calc = DoCalculus(confounded_graph)
        confounders = do_calc.identify_confounders("X", "Y")
        
        assert "Z" in confounders
    
    def test_intervention_no_confounders(self, simple_graph):
        """Test intervention without confounders."""
        np.random.seed(42)
        n = 500
        
        X = np.random.normal(5, 2, n)
        Y = 0.6 * X + np.random.normal(0, 1, n)
        
        data = {"X": X, "Y": Y}
        do_calc = DoCalculus(simple_graph)
        
        # Intervention: set X=8
        effect = do_calc.compute_intervention(data, "X", "Y", 8.0)
        
        assert not np.isnan(effect)
        # Expected Y ≈ 0.6 * 8 = 4.8 (plus mean offset)
        assert 3 < effect < 7


class TestCounterfactualEngine:
    """Test counterfactual reasoning."""
    
    @pytest.fixture
    def simple_graph(self):
        """Graph: sleep -> performance"""
        graph = CausalGraph()
        graph.add_variable("sleep")
        graph.add_variable("performance")
        graph.add_edge("sleep", "performance", strength=0.7)
        return graph
    
    def test_counterfactual_computation(self, simple_graph):
        """Test basic counterfactual."""
        np.random.seed(42)
        n = 200
        
        sleep = np.random.normal(7, 1, n)
        performance = 0.7 * sleep + np.random.normal(5, 0.5, n)
        
        data = {"sleep": sleep, "performance": performance}
        
        cf_engine = CounterfactualEngine(simple_graph)
        
        # Observed: sleep=6, performance=8
        observed = {"sleep": 6.0, "performance": 8.0}
        
        # What if sleep was 8?
        intervention = {"sleep": 8.0}
        
        counterfactual = cf_engine.compute_counterfactual(
            data, observed, intervention, "performance"
        )
        
        assert not np.isnan(counterfactual)
        # Should be higher than observed due to more sleep
        assert counterfactual > observed["performance"]


class TestInterventionOptimizer:
    """Test intervention optimization."""
    
    @pytest.fixture
    def education_graph(self):
        """Simple education graph."""
        graph = CausalGraph()
        graph.add_variable("study_hours")
        graph.add_variable("test_score")
        graph.add_edge("study_hours", "test_score", strength=0.8)
        return graph
    
    def test_find_optimal_intervention(self, education_graph):
        """Test finding optimal study hours."""
        np.random.seed(42)
        n = 300
        
        study = np.random.uniform(1, 5, n)
        score = 0.8 * study + np.random.normal(60, 5, n)
        
        data = {"study_hours": study, "test_score": score}
        
        optimizer = InterventionOptimizer(education_graph)
        
        result = optimizer.find_optimal_intervention(
            data,
            treatment_var="study_hours",
            outcome_var="test_score",
            outcome_target=80.0,
            treatment_range=(1.0, 6.0),
            step=0.5
        )
        
        assert result["optimal_treatment"] is not None
        # To get score of 80 with strength 0.8, need about (80-60)/0.8 = 25 study hours
        # But range is limited, so will be at upper end
        assert result["optimal_treatment"] >= 4.0
    
    def test_compare_interventions(self, education_graph):
        """Test comparing multiple interventions."""
        np.random.seed(42)
        n = 200
        
        study = np.random.uniform(1, 5, n)
        score = 0.8 * study + np.random.normal(60, 5, n)
        
        data = {"study_hours": study, "test_score": score}
        
        optimizer = InterventionOptimizer(education_graph)
        
        interventions = [
            {"study_hours": 2.0},
            {"study_hours": 3.0},
            {"study_hours": 4.0},
        ]
        
        results = optimizer.compare_interventions(
            data, interventions, "test_score"
        )
        
        assert len(results) == 3
        # Higher study hours should give higher expected score
        assert results[0]["expected_outcome"] < results[2]["expected_outcome"]


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_graph(self):
        """Test operations on empty graph."""
        graph = CausalGraph()
        
        assert graph.get_parents("nonexistent") == []
        assert graph.find_paths("A", "B") == []
        assert graph.is_valid()  # Empty graph is valid DAG
    
    def test_self_loop_prevention(self):
        """Test that self-loops are not allowed."""
        graph = CausalGraph()
        graph.add_variable("X")
        
        # NetworkX should handle this
        graph.add_edge("X", "X")
        
        # Self-loop makes it not a valid DAG
        assert not graph.is_valid()
    
    def test_isolated_nodes(self):
        """Test graph with isolated nodes."""
        graph = CausalGraph()
        graph.add_variable("A")
        graph.add_variable("B")  # Isolated
        graph.add_variable("C")
        graph.add_edge("A", "C")
        
        assert graph.is_valid()
        assert graph.get_parents("B") == []
        assert graph.get_children("B") == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
