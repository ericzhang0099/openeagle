#!/usr/bin/env python3
"""
Causal Inference Example for VisionClaw

Demonstrates how to:
1. Build causal graphs from domain knowledge
2. Discover causal relationships from data
3. Compute intervention effects (do-calculus)
4. Run counterfactual analysis
5. Optimize intervention strategies
"""

import numpy as np
from app.core.causal import (
    CausalGraph,
    CausalDiscovery,
    DoCalculus,
    CounterfactualEngine,
    InterventionOptimizer,
)


def example_education_causal_graph():
    """
    Example: Build causal graph for education scenario.
    
    Relationships:
    - Sleep -> Mood -> Learning
    - Sleep -> Fatigue -> Learning
    - Interest -> Engagement -> Learning
    - Parent_Involvement -> Engagement
    """
    print("\n" + "=" * 60)
    print("Example 1: Education Causal Graph")
    print("=" * 60)
    
    graph = CausalGraph()
    
    # Add variables
    variables = [
        ("sleep_quality", "continuous"),
        ("mood_score", "continuous"),
        ("fatigue_level", "continuous"),
        ("interest_level", "continuous"),
        ("engagement", "continuous"),
        ("parent_involvement", "continuous"),
        ("learning_efficiency", "continuous"),
    ]
    
    for name, vtype in variables:
        graph.add_variable(name, vtype)
    
    # Add causal edges (from educational psychology research)
    edges = [
        # Sleep affects mood and fatigue
        ("sleep_quality", "mood_score", 0.7),
        ("sleep_quality", "fatigue_level", -0.8),
        
        # Mood and fatigue affect learning
        ("mood_score", "learning_efficiency", 0.6),
        ("fatigue_level", "learning_efficiency", -0.5),
        
        # Interest and parent involvement affect engagement
        ("interest_level", "engagement", 0.8),
        ("parent_involvement", "engagement", 0.5),
        
        # Engagement affects learning
        ("engagement", "learning_efficiency", 0.7),
        
        # Mood affects engagement
        ("mood_score", "engagement", 0.4),
    ]
    
    for source, target, strength in edges:
        graph.add_edge(source, target, strength=strength)
    
    print(f"\nVariables: {len(graph.variables)}")
    print(f"Causal edges: {len(graph.edges)}")
    print(f"\nKey relationships:")
    for edge in graph.edges.values():
        print(f"  {edge.source} -> {edge.target} (strength: {edge.strength:+.2f})")
    
    # Show causal paths
    print(f"\nCausal paths from sleep to learning:")
    paths = graph.find_paths("sleep_quality", "learning_efficiency")
    for i, path in enumerate(paths, 1):
        print(f"  Path {i}: {' -> '.join(path)}")
    
    return graph


def example_discover_from_data():
    """Example: Discover causal relationships from observational data."""
    print("\n" + "=" * 60)
    print("Example 2: Causal Discovery from Data")
    print("=" * 60)
    
    # Generate synthetic data (in real scenario, this comes from sensors)
    np.random.seed(42)
    n_days = 100
    
    # Simulate: sleep affects next day's mood and performance
    sleep = np.random.normal(7.5, 1.2, n_days)
    mood = 0.6 * sleep + np.random.normal(0, 0.8, n_days)
    fatigue = -0.7 * sleep + np.random.normal(8, 1.5, n_days)
    learning = 0.5 * mood - 0.4 * fatigue + np.random.normal(5, 1, n_days)
    
    data = {
        'sleep': sleep,
        'mood': mood,
        'fatigue': fatigue,
        'learning': learning
    }
    
    print(f"\nData: {n_days} days of observations")
    for var, values in data.items():
        print(f"  {var}: mean={values.mean():.2f}, std={values.std():.2f}")
    
    # Discover using Granger causality (for time series)
    discovery = CausalDiscovery(method="granger")
    discovered_graph = discovery.granger_causality(data, max_lag=2)
    
    print(f"\nDiscovered causal relationships:")
    for edge in discovered_graph.edges.values():
        print(f"  {edge.source} -> {edge.target}")
        print(f"    Confidence: {edge.confidence:.2f}")
    
    return discovered_graph


def example_intervention_analysis():
    """Example: What happens if we intervene on sleep?"""
    print("\n" + "=" * 60)
    print("Example 3: Intervention Analysis (Do-Calculus)")
    print("=" * 60)
    
    # Build graph
    graph = example_education_causal_graph()
    
    # Generate data
    np.random.seed(42)
    n = 1000
    
    sleep = np.random.normal(7, 1.5, n)
    mood = 0.7 * sleep + np.random.normal(0, 0.5, n)
    fatigue = -0.8 * sleep + np.random.normal(5, 1, n)
    learning = 0.6 * mood - 0.5 * fatigue + np.random.normal(5, 0.8, n)
    
    data = {
        'sleep_quality': sleep,
        'mood_score': mood,
        'fatigue_level': fatigue,
        'learning_efficiency': learning
    }
    
    do_calc = DoCalculus(graph)
    
    # Question: What is the effect of ensuring 8 hours of sleep?
    print("\nQuestion: If we ensure child sleeps 8 hours, what happens to learning?")
    
    effect_6h = do_calc.compute_intervention(
        data, 'sleep_quality', 'learning_efficiency', 6.0
    )
    effect_8h = do_calc.compute_intervention(
        data, 'sleep_quality', 'learning_efficiency', 8.0
    )
    effect_9h = do_calc.compute_intervention(
        data, 'sleep_quality', 'learning_efficiency', 9.0
    )
    
    print(f"\nExpected learning efficiency:")
    print(f"  With 6 hours sleep: {effect_6h:.2f}")
    print(f"  With 8 hours sleep: {effect_8h:.2f}")
    print(f"  With 9 hours sleep: {effect_9h:.2f}")
    print(f"\nInsight: 8h vs 6h gives +{effect_8h - effect_6h:.2f} improvement")
    
    return do_calc


def example_counterfactual():
    """Example: What would have happened if...?"""
    print("\n" + "=" * 60)
    print("Example 4: Counterfactual Analysis")
    print("=" * 60)
    
    graph = example_education_causal_graph()
    
    # Generate data
    np.random.seed(42)
    n = 100
    
    sleep = np.random.normal(6.5, 1, n)  # Poor sleep
    mood = 0.7 * sleep + np.random.normal(0, 0.5, n)
    fatigue = -0.8 * sleep + np.random.normal(5, 1, n)
    learning = 0.6 * mood - 0.5 * fatigue + np.random.normal(5, 0.8, n)
    
    data = {
        'sleep_quality': sleep,
        'mood_score': mood,
        'fatigue_level': fatigue,
        'learning_efficiency': learning
    }
    
    cf_engine = CounterfactualEngine(graph)
    
    # Scenario: Child had poor sleep (6h) and low learning score
    observed = {'sleep_quality': 6.0, 'learning_efficiency': 4.5}
    
    # Counterfactual: What if sleep was 8.5 hours?
    intervention = {'sleep_quality': 8.5}
    
    counterfactual = cf_engine.compute_counterfactual(
        data, observed, intervention, 'learning_efficiency'
    )
    
    print(f"\nScenario:")
    print(f"  Observed: Child slept {observed['sleep_quality']:.1f}h")
    print(f"  Learning score: {observed['learning_efficiency']:.1f}/10")
    print(f"\nCounterfactual question:")
    print(f"  What if child had slept {intervention['sleep_quality']:.1f}h instead?")
    print(f"\nAnswer:")
    print(f"  Predicted learning score: {counterfactual:.1f}/10")
    print(f"  Improvement: +{counterfactual - observed['learning_efficiency']:.1f} points")
    
    return counterfactual


def example_optimal_intervention():
    """Example: Find the best intervention strategy."""
    print("\n" + "=" * 60)
    print("Example 5: Optimal Intervention Strategy")
    print("=" * 60)
    
    graph = example_education_causal_graph()
    
    # Generate data
    np.random.seed(42)
    n = 500
    
    sleep = np.random.normal(7, 1.5, n)
    mood = 0.7 * sleep + np.random.normal(0, 0.5, n)
    fatigue = -0.8 * sleep + np.random.normal(5, 1, n)
    interest = np.random.normal(6, 2, n)
    engagement = 0.8 * interest + 0.4 * mood + np.random.normal(0, 0.5, n)
    parent = np.random.normal(5, 2, n)
    learning = (0.6 * mood - 0.5 * fatigue + 
                0.7 * engagement + np.random.normal(5, 0.8, n))
    
    data = {
        'sleep_quality': sleep,
        'mood_score': mood,
        'fatigue_level': fatigue,
        'interest_level': interest,
        'engagement': engagement,
        'parent_involvement': parent,
        'learning_efficiency': learning
    }
    
    optimizer = InterventionOptimizer(graph)
    
    # Goal: Achieve learning score of 8.5
    print("\nGoal: Achieve learning efficiency of 8.5/10")
    print("\nStrategy 1: Adjust sleep duration")
    
    optimal_sleep = optimizer.find_optimal_intervention(
        data,
        treatment_var='sleep_quality',
        outcome_var='learning_efficiency',
        outcome_target=8.5,
        treatment_range=(5.0, 10.0),
        step=0.5
    )
    
    print(f"  Optimal: {optimal_sleep['optimal_treatment']:.1f} hours sleep")
    print(f"  Expected outcome: {optimal_sleep['actual_expected']:.2f}")
    
    print("\nStrategy 2: Increase parent involvement")
    
    optimal_parent = optimizer.find_optimal_intervention(
        data,
        treatment_var='parent_involvement',
        outcome_var='learning_efficiency',
        outcome_target=8.5,
        treatment_range=(3.0, 9.0),
        step=0.5
    )
    
    print(f"  Optimal: Parent involvement level {optimal_parent['optimal_treatment']:.1f}/10")
    print(f"  Expected outcome: {optimal_parent['actual_expected']:.2f}")
    
    print("\nComparison:")
    print(f"  Sleep adjustment: +{optimal_sleep['actual_expected'] - data['learning_efficiency'].mean():.2f}")
    print(f"  Parent involvement: +{optimal_parent['actual_expected'] - data['learning_efficiency'].mean():.2f}")
    print(f"\nRecommendation: {'Sleep' if optimal_sleep['actual_expected'] > optimal_parent['actual_expected'] else 'Parent involvement'} is more effective")


def main():
    """Run all examples."""
    print("=" * 60)
    print("VisionClaw Causal Inference Examples")
    print("=" * 60)
    print("\nThis demonstrates causal reasoning for education scenarios:")
    print("1. Building causal graphs from domain knowledge")
    print("2. Discovering causal relationships from data")
    print("3. Computing intervention effects (do-calculus)")
    print("4. Counterfactual: 'What if we had done X?'")
    print("5. Finding optimal intervention strategies")
    
    example_education_causal_graph()
    example_discover_from_data()
    example_intervention_analysis()
    example_counterfactual()
    example_optimal_intervention()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
    print("\nKey Takeaways for VisionClaw:")
    print("1. Causal graphs model 'why' not just 'what'")
    print("2. Do-calculus predicts effects of interventions")
    print("3. Counterfactuals enable personalized recommendations")
    print("4. Optimization finds best action given constraints")
    print("=" * 60)


if __name__ == "__main__":
    main()
