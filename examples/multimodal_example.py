#!/usr/bin/env python3
"""
Multimodal Fusion Example for VisionClaw

Demonstrates how to fuse vision, audio, and temporal features
for student state recognition (e.g., focused, distracted, tired).
"""

import torch
import numpy as np
from app.core.fusion import (
    ModalityFeatures,
    EarlyFusion,
    LateFusion,
    AttentionFusion,
    MultimodalClassifier,
)


def simulate_student_data(batch_size=4, seq_len=30):
    """
    Simulate multimodal data from a student learning session.
    
    30 seconds of observation, with features extracted every second.
    """
    # Vision features: posture, facial expression, gaze direction
    # Shape: (batch, seq_len, 512)
    vision = torch.randn(batch_size, seq_len, 512)
    
    # Add pattern: student looking away more in distracted samples
    for i in range(batch_size):
        if i % 2 == 1:  # Simulate distracted student
            vision[i, 15:25, 400:512] = 0.5  # Looking away pattern
    
    # Audio features: speech rate, tone, silence periods
    # Shape: (batch, seq_len, 128)
    audio = torch.randn(batch_size, seq_len, 128)
    
    # Add pattern: less speech when tired
    for i in range(batch_size):
        if i >= 2:  # Simulate tired student
            audio[i, :, :] *= 0.3  # Quieter/less speech
    
    # Temporal features: time of day, session duration, task progress
    # Shape: (batch, seq_len, 64)
    temporal = torch.randn(batch_size, seq_len, 64)
    
    # Add time-of-day patterns
    for i in range(batch_size):
        if i % 3 == 0:  # Morning
            temporal[i, :, 0] = 0.2  # Early in day
        elif i % 3 == 1:  # Afternoon
            temporal[i, :, 0] = 0.5  # Mid day
        else:  # Evening
            temporal[i, :, 0] = 0.8  # Late in day
    
    return ModalityFeatures(
        vision=vision,
        audio=audio,
        temporal=temporal
    )


def example_early_fusion():
    """Example: Early Fusion strategy."""
    print("\n" + "=" * 60)
    print("Example 1: Early Fusion")
    print("=" * 60)
    
    features = simulate_student_data()
    
    # Early Fusion: Concatenate at input level
    fusion = EarlyFusion(
        vision_dim=512,
        audio_dim=128,
        text_dim=768,  # Not used in this example
        temporal_dim=64,
        output_dim=256
    )
    
    output = fusion(features)
    print(f"Input shapes:")
    print(f"  Vision: {features.vision.shape}")
    print(f"  Audio: {features.audio.shape}")
    print(f"  Temporal: {features.temporal.shape}")
    print(f"\nFused output: {output.shape}")
    print(f"Strategy: Concatenate -> Project")
    
    return output


def example_late_fusion():
    """Example: Late Fusion strategy."""
    print("\n" + "=" * 60)
    print("Example 2: Late Fusion")
    print("=" * 60)
    
    features = simulate_student_data()
    
    # Late Fusion: Process separately, then combine
    fusion = LateFusion(
        vision_dim=512,
        audio_dim=128,
        temporal_dim=64,
        hidden_dim=128,
        output_dim=256
    )
    
    output = fusion(features)
    print(f"Input: Same as above")
    print(f"\nFused output: {output.shape}")
    print(f"Strategy: Encode separately -> Weighted combination")
    
    return output


def example_attention_fusion():
    """Example: Attention-based Fusion."""
    print("\n" + "=" * 60)
    print("Example 3: Attention Fusion (Recommended)")
    print("=" * 60)
    
    features = simulate_student_data()
    
    # Attention Fusion: Learn cross-modal relationships
    fusion = AttentionFusion(
        vision_dim=512,
        audio_dim=128,
        temporal_dim=64,
        hidden_dim=256,
        num_heads=8,
        num_layers=2
    )
    
    output = fusion(features)
    print(f"Input: Same as above")
    print(f"\nFused output: {output.shape}")
    print(f"Strategy: Cross-modal attention with modality embeddings")
    print(f"Key advantage: Learns which modalities to focus on for each sample")
    
    return output


def example_student_classifier():
    """Example: Complete student state classifier."""
    print("\n" + "=" * 60)
    print("Example 4: Student State Classification")
    print("=" * 60)
    
    features = simulate_student_data(batch_size=8)
    
    # Classifier: 5 states
    # 0: Focused, 1: Distracted, 2: Tired, 3: Excited, 4: Confused
    classifier = MultimodalClassifier(
        fusion_type="attention",
        num_classes=5,
        hidden_dim=256,
        num_heads=8,
        num_layers=2
    )
    
    logits = classifier(features)
    predictions = logits.argmax(dim=1)
    
    state_names = ["Focused", "Distracted", "Tired", "Excited", "Confused"]
    
    print(f"Batch size: 8 students")
    print(f"\nPredictions:")
    for i, pred in enumerate(predictions):
        print(f"  Student {i+1}: {state_names[pred]} (confidence: {torch.softmax(logits[i], dim=0)[pred]:.2f})")
    
    return predictions


def example_missing_modality():
    """Example: Handling missing modalities."""
    print("\n" + "=" * 60)
    print("Example 5: Handling Missing Modalities")
    print("=" * 60)
    
    # Scenario: Audio is not available (e.g., microphone off)
    features = ModalityFeatures(
        vision=torch.randn(2, 30, 512),
        audio=None,  # Missing!
        temporal=torch.randn(2, 30, 64)
    )
    
    classifier = MultimodalClassifier(
        fusion_type="late",  # Late fusion handles missing data better
        num_classes=5
    )
    
    logits = classifier(features)
    print(f"Audio modality: MISSING")
    print(f"Available: Vision + Temporal")
    print(f"Output shape: {logits.shape}")
    print(f"Status: Successfully classified using available modalities")


def main():
    """Run all examples."""
    print("=" * 60)
    print("VisionClaw Multimodal Fusion Examples")
    print("=" * 60)
    print("\nThis demonstrates three fusion strategies for combining")
    print("vision (posture/expression), audio (speech/tone), and")
    print("temporal (time/session) features for student monitoring.")
    
    example_early_fusion()
    example_late_fusion()
    example_attention_fusion()
    example_student_classifier()
    example_missing_modality()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("1. Early Fusion: Simple, but requires aligned data")
    print("2. Late Fusion: Robust to missing data, modular")
    print("3. Attention Fusion: Best performance, learns cross-modal relations")
    print("4. For VisionClaw: Attention Fusion recommended for accuracy")
    print("=" * 60)


if __name__ == "__main__":
    main()
