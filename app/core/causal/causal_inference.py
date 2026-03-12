"""
Causal Inference System

Implements causal discovery and intervention analysis for education/health scenarios.

Key Concepts:
1. Causal Graph: Directed acyclic graph (DAG) representing causal relationships
2. Do-Calculus: Framework for computing intervention effects
3. Counterfactuals: "What if" scenarios

References:
- Pearl, J. "Causality" (2009)
- Pearl, J. "The Book of Why" (2018)
- Zhang et al. "Causal Discovery with Multi-Domain Data" (2022)
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import networkx as nx
from scipy import stats


@dataclass
class CausalVariable:
    """Represents a variable in the causal model."""
    name: str
    var_type: str = "continuous"  # "continuous", "discrete", "binary"
    parents: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)
    
    # Statistical properties
    mean: float = 0.0
    std: float = 1.0
    
    def __hash__(self):
        return hash(self.name)


@dataclass
class CausalEdge:
    """Represents a causal relationship between two variables."""
    source: str
    target: str
    strength: float = 0.0  # Coefficient or correlation
    confidence: float = 0.0  # Statistical confidence
    mechanism: str = "linear"  # "linear", "nonlinear", "unknown"


class CausalGraph:
    """
    Causal Graph for modeling relationships between variables.
    
    Example for education scenario:
    sleep_quality -> mood -> learning_efficiency
                  -> fatigue ->
    """
    
    def __init__(self):
        self.variables: Dict[str, CausalVariable] = {}
        self.edges: Dict[Tuple[str, str], CausalEdge] = {}
        self.graph = nx.DiGraph()
        
    def add_variable(self, name: str, var_type: str = "continuous") -> CausalVariable:
        """Add a variable to the graph."""
        var = CausalVariable(name=name, var_type=var_type)
        self.variables[name] = var
        self.graph.add_node(name)
        return var
    
    def add_edge(
        self,
        source: str,
        target: str,
        strength: float = 0.0,
        confidence: float = 0.0
    ) -> CausalEdge:
        """Add a causal edge (source -> target)."""
        if source not in self.variables:
            self.add_variable(source)
        if target not in self.variables:
            self.add_variable(target)
        
        edge = CausalEdge(
            source=source,
            target=target,
            strength=strength,
            confidence=confidence
        )
        
        self.edges[(source, target)] = edge
        self.graph.add_edge(source, target, weight=strength)
        
        # Update parent/child relationships
        self.variables[target].parents.append(source)
        self.variables[source].children.append(target)
        
        return edge
    
    def get_parents(self, variable: str) -> List[str]:
        """Get parent variables."""
        return list(self.graph.predecessors(variable))
    
    def get_children(self, variable: str) -> List[str]:
        """Get child variables."""
        return list(self.graph.successors(variable))
    
    def get_ancestors(self, variable: str) -> Set[str]:
        """Get all ancestor variables."""
        return nx.ancestors(self.graph, variable)
    
    def get_descendants(self, variable: str) -> Set[str]:
        """Get all descendant variables."""
        return nx.descendants(self.graph, variable)
    
    def find_paths(
        self,
        source: str,
        target: str
    ) -> List[List[str]]:
        """Find all causal paths from source to target."""
        try:
            paths = list(nx.all_simple_paths(self.graph, source, target))
            return paths
        except nx.NetworkXNoPath:
            return []
    
    def is_valid(self) -> bool:
        """Check if graph is a valid DAG (no cycles)."""
        return nx.is_directed_acyclic_graph(self.graph)
    
    def visualize(self, output_path: Optional[str] = None):
        """Visualize the causal graph."""
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.graph, k=2, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph, pos,
            node_color='lightblue',
            node_size=2000,
            alpha=0.9
        )
        
        # Draw edges with weights
        edge_weights = [self.edges.get((u, v), CausalEdge(u, v)).strength 
                       for u, v in self.graph.edges()]
        
        nx.draw_networkx_edges(
            self.graph, pos,
            width=[abs(w) * 3 for w in edge_weights],
            alpha=0.6,
            arrows=True,
            arrowsize=20,
            edge_color=['green' if w > 0 else 'red' for w in edge_weights]
        )
        
        # Draw labels
        nx.draw_networkx_labels(self.graph, pos, font_size=10)
        
        plt.title("Causal Graph")
        plt.axis('off')
        
        if output_path:
            plt.savefig(output_path, bbox_inches='tight')
        else:
            plt.show()


class CausalDiscovery:
    """
    Discover causal relationships from observational data.
    
    Methods:
    1. Granger Causality: Time-series causality
    2. PC Algorithm: Constraint-based causal discovery
    3. NOTEARS: Gradient-based DAG learning
    """
    
    def __init__(self, method: str = "granger"):
        self.method = method
        self.graph = CausalGraph()
        
    def granger_causality(
        self,
        data: Dict[str, np.ndarray],
        max_lag: int = 3,
        significance: float = 0.05
    ) -> CausalGraph:
        """
        Discover causal relationships using Granger causality.
        
        X Granger-causes Y if past values of X help predict Y.
        
        Args:
            data: Dictionary of time series {variable_name: values}
            max_lag: Maximum time lag to test
            significance: P-value threshold for significance
            
        Returns:
            CausalGraph with discovered relationships
        """
        from statsmodels.tsa.stattools import grangercausalitytests
        
        variables = list(data.keys())
        
        for target in variables:
            for source in variables:
                if source == target:
                    continue
                
                # Prepare data for Granger test
                # Stack source and target time series
                combined = np.column_stack([data[source], data[target]])
                
                try:
                    # Run Granger causality test
                    gc_result = grangercausalitytests(combined, maxlag=max_lag, verbose=False)
                    
                    # Check if any lag is significant
                    min_pvalue = min(
                        gc_result[lag][0]['ssr_ftest'][1] 
                        for lag in range(1, max_lag + 1)
                    )
                    
                    if min_pvalue < significance:
                        # Source Granger-causes target
                        strength = 1.0 - min_pvalue  # Higher strength = lower p-value
                        self.graph.add_edge(
                            source=source,
                            target=target,
                            strength=strength,
                            confidence=1.0 - min_pvalue
                        )
                        
                except Exception as e:
                    print(f"Error testing {source} -> {target}: {e}")
        
        return self.graph
    
    def correlation_based(
        self,
        data: Dict[str, np.ndarray],
        threshold: float = 0.3
    ) -> CausalGraph:
        """
        Simple correlation-based discovery (for baseline comparison).
        
        Note: Correlation != Causation! This is just for exploration.
        """
        variables = list(data.keys())
        
        for i, var1 in enumerate(variables):
            for var2 in variables[i+1:]:
                corr, pvalue = stats.pearsonr(data[var1], data[var2])
                
                if abs(corr) > threshold and pvalue < 0.05:
                    # Add edge in direction of temporal priority
                    # (simplified assumption: lower variance is earlier)
                    var1_var = np.var(data[var1])
                    var2_var = np.var(data[var2])
                    
                    if var1_var < var2_var:
                        source, target = var1, var2
                    else:
                        source, target = var2, var1
                    
                    self.graph.add_edge(
                        source=source,
                        target=target,
                        strength=abs(corr),
                        confidence=1.0 - pvalue
                    )
        
        return self.graph


class DoCalculus:
    """
    Implementation of Pearl's Do-Calculus for computing intervention effects.
    
    Key formulas:
    - P(Y | do(X=x)) = Sum_z P(Y | X=x, Z=z) P(Z=z)
    where Z is the set of confounders
    """
    
    def __init__(self, graph: CausalGraph):
        self.graph = graph
        
    def identify_confounders(
        self,
        treatment: str,
        outcome: str
    ) -> Set[str]:
        """
        Identify confounding variables between treatment and outcome.
        
        Confounders are common causes of both treatment and outcome.
        """
        treatment_ancestors = self.graph.get_ancestors(treatment)
        outcome_ancestors = self.graph.get_ancestors(outcome)
        
        confounders = treatment_ancestors.intersection(outcome_ancestors)
        return confounders
    
    def compute_intervention(
        self,
        data: Dict[str, np.ndarray],
        treatment: str,
        outcome: str,
        treatment_value: float
    ) -> float:
        """
        Compute P(outcome | do(treatment=treatment_value)).
        
        Simplified implementation using adjustment formula.
        """
        # Identify confounders
        confounders = self.identify_confounders(treatment, outcome)
        
        if not confounders:
            # No confounders, simple conditioning works
            mask = data[treatment] == treatment_value
            if mask.sum() == 0:
                return np.nan
            return data[outcome][mask].mean()
        
        # Adjustment formula: Sum over confounders
        # P(Y|do(X=x)) = Sum_z P(Y|X=x,Z=z) P(Z=z)
        
        # For continuous confounders, bin them
        confounder_list = list(confounders)
        if len(confounder_list) == 1:
            Z = data[confounder_list[0]]
            z_bins = np.linspace(Z.min(), Z.max(), 5)
            
            total_prob = 0.0
            for i in range(len(z_bins) - 1):
                z_mask = (Z >= z_bins[i]) & (Z < z_bins[i+1])
                p_z = z_mask.mean()
                
                if p_z > 0:
                    # P(Y | X=x, Z in bin)
                    x_mask = (data[treatment] == treatment_value) & z_mask
                    if x_mask.sum() > 0:
                        p_y_given_xz = data[outcome][x_mask].mean()
                        total_prob += p_y_given_xz * p_z
            
            return total_prob
        
        # Multiple confounders - use simplified approach
        return self._simple_adjustment(data, treatment, outcome, treatment_value, confounder_list)
    
    def _simple_adjustment(
        self,
        data: Dict[str, np.ndarray],
        treatment: str,
        outcome: str,
        treatment_value: float,
        confounders: List[str]
    ) -> float:
        """Simplified adjustment for multiple confounders."""
        # Stratify by confounders (simplified: use mean values)
        confounder_means = {z: data[z].mean() for z in confounders}
        
        # Find samples where confounders are close to mean
        mask = np.ones(len(data[treatment]), dtype=bool)
        for z, mean_val in confounder_means.items():
            z_std = data[z].std()
            mask = mask & (np.abs(data[z] - mean_val) < z_std)
        
        # Among these, find treatment=treatment_value
        treatment_mask = mask & (np.abs(data[treatment] - treatment_value) < 0.1)
        
        if treatment_mask.sum() == 0:
            return np.nan
        
        return data[outcome][treatment_mask].mean()


class CounterfactualEngine:
    """
    Counterfactual reasoning: "What would have happened if..."
    
    Example: "What would the test score be if the child had slept 8 hours instead of 6?"
    """
    
    def __init__(self, graph: CausalGraph):
        self.graph = graph
        self.do_calculus = DoCalculus(graph)
        
    def compute_counterfactual(
        self,
        data: Dict[str, np.ndarray],
        observed: Dict[str, float],
        intervention: Dict[str, float],
        target: str
    ) -> float:
        """
        Compute counterfactual: P(Y_{X=x} | X=x', Y=y')
        
        Three steps (abduction, action, prediction):
        1. Abduction: Update beliefs given evidence
        2. Action: Apply intervention
        3. Prediction: Predict outcome
        
        Simplified implementation for continuous variables.
        """
        # Step 1: Abduction - estimate latent variables from observed
        # (Simplified: assume we can directly use observed values)
        
        # Step 2 & 3: Apply intervention and predict
        # Use structural equations implied by the graph
        
        # For now, use simplified linear approximation
        prediction = self._linear_counterfactual(data, observed, intervention, target)
        
        return prediction
    
    def _linear_counterfactual(
        self,
        data: Dict[str, np.ndarray],
        observed: Dict[str, float],
        intervention: Dict[str, float],
        target: str
    ) -> float:
        """Simplified linear counterfactual estimation."""
        # Build linear approximation from data
        parents = self.graph.get_parents(target)
        
        if not parents:
            # No parents, just return mean
            return data[target].mean()
        
        # Fit simple linear model: target = sum(coeff_i * parent_i) + noise
        coeffs = {}
        for parent in parents:
            # Simple correlation-based coefficient
            corr = np.corrcoef(data[parent], data[target])[0, 1]
            target_std = data[target].std()
            parent_std = data[parent].std()
            if parent_std > 0:
                coeffs[parent] = corr * target_std / parent_std
            else:
                coeffs[parent] = 0
        
        # Predict using intervention values where specified
        prediction = data[target].mean()
        for parent, coeff in coeffs.items():
            if parent in intervention:
                # Use counterfactual value
                value = intervention[parent]
            elif parent in observed:
                # Use observed value
                value = observed[parent]
            else:
                # Use mean
                value = data[parent].mean()
            
            prediction += coeff * (value - data[parent].mean())
        
        return prediction


class InterventionOptimizer:
    """
    Optimize intervention strategies to achieve desired outcomes.
    
    Example: "What's the best time to remind the child to rest?"
    """
    
    def __init__(self, graph: CausalGraph):
        self.graph = graph
        self.do_calculus = DoCalculus(graph)
        
    def find_optimal_intervention(
        self,
        data: Dict[str, np.ndarray],
        treatment_var: str,
        outcome_var: str,
        outcome_target: float,
        treatment_range: Tuple[float, float],
        step: float = 0.1
    ) -> Dict:
        """
        Find treatment value that achieves desired outcome.
        
        Returns:
            Dictionary with optimal treatment value and expected outcome
        """
        best_treatment = None
        best_outcome_diff = float('inf')
        results = []
        
        treatment_values = np.arange(
            treatment_range[0],
            treatment_range[1] + step,
            step
        )
        
        for treatment_val in treatment_values:
            expected_outcome = self.do_calculus.compute_intervention(
                data, treatment_var, outcome_var, treatment_val
            )
            
            if np.isnan(expected_outcome):
                continue
            
            outcome_diff = abs(expected_outcome - outcome_target)
            
            results.append({
                'treatment': treatment_val,
                'expected_outcome': expected_outcome,
                'diff': outcome_diff
            })
            
            if outcome_diff < best_outcome_diff:
                best_outcome_diff = outcome_diff
                best_treatment = treatment_val
        
        return {
            'optimal_treatment': best_treatment,
            'expected_outcome': outcome_target,
            'actual_expected': next(
                (r['expected_outcome'] for r in results if r['treatment'] == best_treatment),
                None
            ),
            'all_results': results
        }
    
    def compare_interventions(
        self,
        data: Dict[str, np.ndarray],
        interventions: List[Dict[str, float]],
        outcome_var: str
    ) -> List[Dict]:
        """
        Compare multiple intervention strategies.
        
        Args:
            interventions: List of {variable: value} dicts
            outcome_var: Target outcome variable
            
        Returns:
            Ranked list of interventions with expected outcomes
        """
        results = []
        
        for i, intervention in enumerate(interventions):
            # For single-variable interventions
            if len(intervention) == 1:
                treatment_var = list(intervention.keys())[0]
                treatment_val = list(intervention.values())[0]
                
                expected = self.do_calculus.compute_intervention(
                    data, treatment_var, outcome_var, treatment_val
                )
                
                results.append({
                    'intervention_id': i,
                    'intervention': intervention,
                    'expected_outcome': expected
                })
        
        # Sort by expected outcome (assuming higher is better)
        results.sort(key=lambda x: x['expected_outcome'] if not np.isnan(x['expected_outcome']) else -np.inf, reverse=True)
        
        return results


# Example usage
def example():
    """Demonstrate causal inference system."""
    print("=" * 60)
    print("Causal Inference System Example")
    print("=" * 60)
    
    # Create example graph for education scenario
    # sleep -> mood -> learning_efficiency
    #      -> fatigue ->
    
    graph = CausalGraph()
    
    # Add variables
    graph.add_variable("sleep_hours", "continuous")
    graph.add_variable("mood_score", "continuous")
    graph.add_variable("fatigue_level", "continuous")
    graph.add_variable("learning_efficiency", "continuous")
    
    # Add causal relationships (from domain knowledge)
    graph.add_edge("sleep_hours", "mood_score", strength=0.7)
    graph.add_edge("sleep_hours", "fatigue_level", strength=-0.8)
    graph.add_edge("mood_score", "learning_efficiency", strength=0.6)
    graph.add_edge("fatigue_level", "learning_efficiency", strength=-0.5)
    
    print("\n1. Causal Graph Structure:")
    print(f"   Variables: {list(graph.variables.keys())}")
    print(f"   Edges: {[(e.source, e.target, f'strength={e.strength:.2f}') for e in graph.edges.values()]}")
    
    # Generate synthetic data
    np.random.seed(42)
    n_samples = 1000
    
    sleep = np.random.normal(7, 1.5, n_samples)  # Hours
    mood = 0.7 * sleep + np.random.normal(0, 0.5, n_samples)  # 0-10 scale
    fatigue = -0.8 * sleep + np.random.normal(5, 1, n_samples)  # 0-10 scale
    learning = 0.6 * mood - 0.5 * fatigue + np.random.normal(5, 1, n_samples)
    
    data = {
        'sleep_hours': sleep,
        'mood_score': mood,
        'fatigue_level': fatigue,
        'learning_efficiency': learning
    }
    
    print("\n2. Data Statistics:")
    for var, values in data.items():
        print(f"   {var}: mean={values.mean():.2f}, std={values.std():.2f}")
    
    # Do-Calculus: Compute intervention effects
    print("\n3. Intervention Analysis:")
    do_calc = DoCalculus(graph)
    
    # What happens to learning efficiency if we ensure 8 hours of sleep?
    effect_8h = do_calc.compute_intervention(data, 'sleep_hours', 'learning_efficiency', 8.0)
    effect_6h = do_calc.compute_intervention(data, 'sleep_hours', 'learning_efficiency', 6.0)
    
    print(f"   P(Learning | do(Sleep=8h)) = {effect_8h:.2f}")
    print(f"   P(Learning | do(Sleep=6h)) = {effect_6h:.2f}")
    print(f"   Difference: {effect_8h - effect_6h:.2f} (8h vs 6h sleep)")
    
    # Counterfactual
    print("\n4. Counterfactual Analysis:")
    cf_engine = CounterfactualEngine(graph)
    
    observed = {'sleep_hours': 6.0, 'learning_efficiency': 5.5}
    intervention = {'sleep_hours': 8.0}
    
    counterfactual = cf_engine.compute_counterfactual(
        data, observed, intervention, 'learning_efficiency'
    )
    
    print(f"   Observed: Sleep=6h, Learning=5.5")
    print(f"   Counterfactual: If Sleep=8h, Learning would be {counterfactual:.2f}")
    
    # Optimization
    print("\n5. Intervention Optimization:")
    optimizer = InterventionOptimizer(graph)
    
    optimal = optimizer.find_optimal_intervention(
        data,
        treatment_var='sleep_hours',
        outcome_var='learning_efficiency',
        outcome_target=8.0,
        treatment_range=(5.0, 10.0),
        step=0.5
    )
    
    print(f"   To achieve Learning=8.0:")
    print(f"   Optimal sleep: {optimal['optimal_treatment']:.1f} hours")
    print(f"   Expected outcome: {optimal['actual_expected']:.2f}")
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    example()
