"""
Unit Tests for Multimodal Fusion Engine

Tests cover:
- Feature concatenation and alignment
- All three fusion strategies
- Missing modality handling
- Forward pass correctness
"""

import pytest
import torch
import numpy as np
from app.core.fusion import (
    ModalityFeatures,
    EarlyFusion,
    LateFusion,
    AttentionFusion,
    MultimodalClassifier,
)


class TestModalityFeatures:
    """Test ModalityFeatures dataclass."""
    
    def test_empty_features(self):
        """Test empty feature container."""
        features = ModalityFeatures()
        assert features.get_available_modalities() == []
    
    def test_single_modality(self):
        """Test with single modality."""
        features = ModalityFeatures(
            vision=torch.randn(2, 10, 512)
        )
        assert features.get_available_modalities() == ["vision"]
    
    def test_all_modalities(self):
        """Test with all modalities."""
        features = ModalityFeatures(
            vision=torch.randn(2, 10, 512),
            audio=torch.randn(2, 10, 128),
            text=torch.randn(2, 10, 768),
            temporal=torch.randn(2, 10, 64)
        )
        modalities = features.get_available_modalities()
        assert len(modalities) == 4
        assert "vision" in modalities
        assert "audio" in modalities


class TestEarlyFusion:
    """Test Early Fusion strategy."""
    
    @pytest.fixture
    def fusion(self):
        return EarlyFusion(
            vision_dim=512,
            audio_dim=128,
            temporal_dim=64,
            output_dim=256
        )
    
    def test_forward_pass(self, fusion):
        """Test basic forward pass."""
        features = ModalityFeatures(
            vision=torch.randn(4, 10, 512),
            audio=torch.randn(4, 10, 128),
            temporal=torch.randn(4, 10, 64)
        )
        
        output = fusion(features)
        
        assert output.shape == (4, 10, 256)
        assert not torch.isnan(output).any()
    
    def test_sequence_alignment(self, fusion):
        """Test handling different sequence lengths."""
        features = ModalityFeatures(
            vision=torch.randn(2, 20, 512),    # Longer sequence
            audio=torch.randn(2, 10, 128),     # Shorter sequence
            temporal=torch.randn(2, 15, 64)    # Medium sequence
        )
        
        output = fusion(features)
        
        # Should align to longest (20)
        assert output.shape[1] == 20
    
    def test_missing_modality(self, fusion):
        """Test with missing modalities."""
        features = ModalityFeatures(
            vision=torch.randn(2, 10, 512),
            # audio missing
            temporal=torch.randn(2, 10, 64)
        )
        
        output = fusion(features)
        assert output.shape == (2, 10, 256)
    
    def test_no_modality_error(self, fusion):
        """Test error when no modalities provided."""
        features = ModalityFeatures()
        
        with pytest.raises(ValueError, match="No modalities"):
            fusion(features)


class TestLateFusion:
    """Test Late Fusion strategy."""
    
    @pytest.fixture
    def fusion(self):
        return LateFusion(
            vision_dim=512,
            audio_dim=128,
            temporal_dim=64,
            hidden_dim=128,
            output_dim=256
        )
    
    def test_forward_pass(self, fusion):
        """Test basic forward pass."""
        features = ModalityFeatures(
            vision=torch.randn(4, 10, 512),
            audio=torch.randn(4, 10, 128),
            temporal=torch.randn(4, 10, 64)
        )
        
        output = fusion(features)
        
        assert output.shape == (4, 10, 256)
        assert not torch.isnan(output).any()
    
    def test_modularity(self, fusion):
        """Test that missing modalities don't break other encoders."""
        # Test with only vision
        features_vision_only = ModalityFeatures(
            vision=torch.randn(2, 10, 512)
        )
        output1 = fusion(features_vision_only)
        assert output1.shape == (2, 10, 256)
        
        # Test with only audio
        features_audio_only = ModalityFeatures(
            audio=torch.randn(2, 10, 128)
        )
        output2 = fusion(features_audio_only)
        assert output2.shape == (2, 10, 256)


class TestAttentionFusion:
    """Test Attention-based Fusion."""
    
    @pytest.fixture
    def fusion(self):
        return AttentionFusion(
            vision_dim=512,
            audio_dim=128,
            temporal_dim=64,
            hidden_dim=256,
            num_heads=8,
            num_layers=2
        )
    
    def test_forward_pass(self, fusion):
        """Test basic forward pass."""
        features = ModalityFeatures(
            vision=torch.randn(4, 10, 512),
            audio=torch.randn(4, 10, 128),
            temporal=torch.randn(4, 10, 64)
        )
        
        output = fusion(features)
        
        # Output is pooled over sequence
        assert output.shape == (4, 256)
        assert not torch.isnan(output).any()
    
    def test_modality_embeddings(self, fusion):
        """Test that modality embeddings are applied."""
        features = ModalityFeatures(
            vision=torch.randn(2, 5, 512),
            audio=torch.randn(2, 5, 128)
        )
        
        output = fusion(features)
        assert output.shape == (2, 256)


class TestMultimodalClassifier:
    """Test complete classification pipeline."""
    
    def test_early_fusion_classifier(self):
        """Test classifier with early fusion."""
        classifier = MultimodalClassifier(
            fusion_type="early",
            num_classes=5,
            output_dim=256
        )
        
        features = ModalityFeatures(
            vision=torch.randn(4, 10, 512),
            audio=torch.randn(4, 10, 128)
        )
        
        logits = classifier(features)
        
        assert logits.shape == (4, 5)
        assert not torch.isnan(logits).any()
    
    def test_attention_fusion_classifier(self):
        """Test classifier with attention fusion."""
        classifier = MultimodalClassifier(
            fusion_type="attention",
            num_classes=3,
            hidden_dim=256,
            num_heads=8,
            num_layers=2
        )
        
        features = ModalityFeatures(
            vision=torch.randn(2, 15, 512),
            temporal=torch.randn(2, 15, 64)
        )
        
        logits = classifier(features)
        
        assert logits.shape == (2, 3)
        predictions = logits.argmax(dim=1)
        assert predictions.shape == (2,)
    
    def test_batch_consistency(self):
        """Test that same input gives same output."""
        classifier = MultimodalClassifier(fusion_type="late", num_classes=5)
        
        features = ModalityFeatures(
            vision=torch.randn(2, 10, 512),
            audio=torch.randn(2, 10, 128)
        )
        
        # Run twice
        logits1 = classifier(features)
        logits2 = classifier(features)
        
        assert torch.allclose(logits1, logits2)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_single_batch_item(self):
        """Test with batch size 1."""
        fusion = EarlyFusion(output_dim=128)
        features = ModalityFeatures(
            vision=torch.randn(1, 10, 512),
            audio=torch.randn(1, 10, 128)
        )
        
        output = fusion(features)
        assert output.shape[0] == 1
    
    def test_single_time_step(self):
        """Test with sequence length 1."""
        fusion = LateFusion(output_dim=128)
        features = ModalityFeatures(
            vision=torch.randn(2, 1, 512),
            audio=torch.randn(2, 1, 128)
        )
        
        output = fusion(features)
        assert output.shape[1] == 1
    
    def test_large_dimensions(self):
        """Test with large feature dimensions."""
        fusion = EarlyFusion(
            vision_dim=2048,
            audio_dim=512,
            output_dim=256
        )
        
        features = ModalityFeatures(
            vision=torch.randn(2, 5, 2048),
            audio=torch.randn(2, 5, 512)
        )
        
        output = fusion(features)
        assert output.shape == (2, 5, 256)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
