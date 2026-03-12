"""
Multimodal Fusion Engine

Implements three fusion strategies for vision, audio, and temporal data:
1. Early Fusion: Concatenate features at input level
2. Late Fusion: Combine decisions from each modality
3. Attention Fusion: Learn cross-modal attention weights

References:
- Zadeh et al. "Tensor Fusion Network for Multimodal Sentiment Analysis" (EMNLP 2017)
- Tsai et al. "Multimodal Transformer for Unaligned Multimodal Language Sequences" (ACL 2019)
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ModalityFeatures:
    """Container for features from different modalities."""
    vision: Optional[torch.Tensor] = None      # Shape: (batch, seq_len, vision_dim)
    audio: Optional[torch.Tensor] = None       # Shape: (batch, seq_len, audio_dim)
    text: Optional[torch.Tensor] = None        # Shape: (batch, seq_len, text_dim)
    temporal: Optional[torch.Tensor] = None    # Shape: (batch, seq_len, temp_dim)
    
    def get_available_modalities(self) -> List[str]:
        """Return list of available modalities."""
        modalities = []
        if self.vision is not None:
            modalities.append("vision")
        if self.audio is not None:
            modalities.append("audio")
        if self.text is not None:
            modalities.append("text")
        if self.temporal is not None:
            modalities.append("temporal")
        return modalities


class EarlyFusion(nn.Module):
    """
    Early Fusion: Concatenate features from all modalities at input level.
    
    Pros: Simple, captures low-level correlations
    Cons: Requires aligned data, high dimensionality
    """
    
    def __init__(
        self,
        vision_dim: int = 512,
        audio_dim: int = 128,
        text_dim: int = 768,
        temporal_dim: int = 64,
        output_dim: int = 256,
        dropout: float = 0.3
    ):
        super().__init__()
        self.vision_dim = vision_dim
        self.audio_dim = audio_dim
        self.text_dim = text_dim
        self.temporal_dim = temporal_dim
        self.total_dim = vision_dim + audio_dim + text_dim + temporal_dim
        
        # Projection layer
        self.projection = nn.Sequential(
            nn.Linear(self.total_dim, output_dim * 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(output_dim * 2, output_dim),
            nn.ReLU()
        )
        
    def forward(self, features: ModalityFeatures) -> torch.Tensor:
        """
        Concatenate and project features.
        
        Args:
            features: ModalityFeatures object
            
        Returns:
            Fused features of shape (batch, seq_len, output_dim)
        """
        # Collect available features
        feat_list = []
        
        if features.vision is not None:
            feat_list.append(features.vision)
        if features.audio is not None:
            feat_list.append(features.audio)
        if features.text is not None:
            feat_list.append(features.text)
        if features.temporal is not None:
            feat_list.append(features.temporal)
        
        if not feat_list:
            raise ValueError("No modalities provided")
        
        # Concatenate along feature dimension
        # Handle different sequence lengths by interpolation
        target_len = max(f.shape[1] for f in feat_list)
        aligned_feats = []
        
        for feat in feat_list:
            if feat.shape[1] != target_len:
                # Interpolate to target length
                feat = F.interpolate(
                    feat.transpose(1, 2),
                    size=target_len,
                    mode='linear',
                    align_corners=False
                ).transpose(1, 2)
            aligned_feats.append(feat)
        
        fused = torch.cat(aligned_feats, dim=-1)
        output = self.projection(fused)
        
        return output


class LateFusion(nn.Module):
    """
    Late Fusion: Process each modality separately, then combine decisions.
    
    Pros: Modalities can use different architectures, robust to missing data
    Cons: May miss cross-modal correlations at feature level
    """
    
    def __init__(
        self,
        vision_dim: int = 512,
        audio_dim: int = 128,
        text_dim: int = 768,
        temporal_dim: int = 64,
        hidden_dim: int = 128,
        output_dim: int = 256,
        dropout: float = 0.3
    ):
        super().__init__()
        
        # Modality-specific encoders
        self.vision_encoder = nn.Sequential(
            nn.Linear(vision_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        self.audio_encoder = nn.Sequential(
            nn.Linear(audio_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        self.text_encoder = nn.Sequential(
            nn.Linear(text_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        self.temporal_encoder = nn.Sequential(
            nn.Linear(temporal_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        # Fusion layer (weighted average)
        self.fusion_weight = nn.Parameter(torch.ones(4))
        
        # Final projection
        self.output_proj = nn.Sequential(
            nn.Linear(hidden_dim, output_dim),
            nn.ReLU()
        )
        
    def forward(self, features: ModalityFeatures) -> torch.Tensor:
        """Process each modality and combine."""
        encoded_list = []
        
        if features.vision is not None:
            encoded_list.append(self.vision_encoder(features.vision))
        else:
            encoded_list.append(None)
            
        if features.audio is not None:
            encoded_list.append(self.audio_encoder(features.audio))
        else:
            encoded_list.append(None)
            
        if features.text is not None:
            encoded_list.append(self.text_encoder(features.text))
        else:
            encoded_list.append(None)
            
        if features.temporal is not None:
            encoded_list.append(self.temporal_encoder(features.temporal))
        else:
            encoded_list.append(None)
        
        # Filter out None values
        valid_encoded = [e for e in encoded_list if e is not None]
        
        if not valid_encoded:
            raise ValueError("No modalities provided")
        
        # Align sequence lengths
        target_len = max(e.shape[1] for e in valid_encoded)
        aligned = []
        
        for feat in valid_encoded:
            if feat.shape[1] != target_len:
                feat = F.interpolate(
                    feat.transpose(1, 2),
                    size=target_len,
                    mode='linear',
                    align_corners=False
                ).transpose(1, 2)
            aligned.append(feat)
        
        # Stack and apply softmax weights
        stacked = torch.stack(aligned, dim=-1)  # (batch, seq, hidden, num_modalities)
        weights = F.softmax(self.fusion_weight[:len(aligned)], dim=0)
        
        # Weighted sum
        fused = torch.sum(stacked * weights.view(1, 1, 1, -1), dim=-1)
        output = self.output_proj(fused)
        
        return output


class CrossModalAttention(nn.Module):
    """
    Cross-Modal Attention: Learn attention weights between modalities.
    
    Inspired by "Attention is All You Need" and multimodal transformers.
    """
    
    def __init__(
        self,
        dim: int = 256,
        num_heads: int = 8,
        dropout: float = 0.1
    ):
        super().__init__()
        self.num_heads = num_heads
        self.dim = dim
        self.head_dim = dim // num_heads
        
        assert dim % num_heads == 0, "dim must be divisible by num_heads"
        
        # Multi-head attention
        self.q_proj = nn.Linear(dim, dim)
        self.k_proj = nn.Linear(dim, dim)
        self.v_proj = nn.Linear(dim, dim)
        self.out_proj = nn.Linear(dim, dim)
        
        self.dropout = nn.Dropout(dropout)
        self.scale = self.head_dim ** -0.5
        
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Cross-modal attention.
        
        Args:
            query: (batch, seq_q, dim)
            key: (batch, seq_k, dim)
            value: (batch, seq_v, dim)
            mask: Optional attention mask
            
        Returns:
            Attention output: (batch, seq_q, dim)
        """
        batch_size = query.shape[0]
        
        # Project and reshape for multi-head
        Q = self.q_proj(query).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.k_proj(key).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.v_proj(value).view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) * self.scale
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        # Apply attention to values
        attn_output = torch.matmul(attn_weights, V)
        
        # Concatenate heads
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, -1, self.dim)
        
        output = self.out_proj(attn_output)
        
        return output


class AttentionFusion(nn.Module):
    """
    Attention-based Fusion: Use transformers to learn cross-modal interactions.
    
    This is the most sophisticated fusion approach.
    """
    
    def __init__(
        self,
        vision_dim: int = 512,
        audio_dim: int = 128,
        text_dim: int = 768,
        temporal_dim: int = 64,
        hidden_dim: int = 256,
        num_heads: int = 8,
        num_layers: int = 4,
        dropout: float = 0.1
    ):
        super().__init__()
        
        # Modality-specific projections to common dimension
        self.vision_proj = nn.Linear(vision_dim, hidden_dim)
        self.audio_proj = nn.Linear(audio_dim, hidden_dim)
        self.text_proj = nn.Linear(text_dim, hidden_dim)
        self.temporal_proj = nn.Linear(temporal_dim, hidden_dim)
        
        # Positional encoding
        self.pos_encoding = PositionalEncoding(hidden_dim, dropout)
        
        # Transformer layers with cross-modal attention
        self.layers = nn.ModuleList([
            TransformerLayer(hidden_dim, num_heads, dropout)
            for _ in range(num_layers)
        ])
        
        # Modality type embeddings
        self.modality_embeddings = nn.Embedding(4, hidden_dim)
        
    def forward(self, features: ModalityFeatures) -> torch.Tensor:
        """
        Fuse modalities using cross-modal attention.
        
        Args:
            features: ModalityFeatures object
            
        Returns:
            Fused features
        """
        batch_size = None
        projections = []
        modality_ids = []
        
        # Project each modality and add type embedding
        if features.vision is not None:
            batch_size = features.vision.shape[0]
            proj = self.vision_proj(features.vision)
            proj = proj + self.modality_embeddings(torch.zeros(proj.shape[0], proj.shape[1], dtype=torch.long, device=proj.device))
            projections.append(proj)
            modality_ids.append(0)
            
        if features.audio is not None:
            batch_size = features.audio.shape[0] if batch_size is None else batch_size
            proj = self.audio_proj(features.audio)
            proj = proj + self.modality_embeddings(torch.ones(proj.shape[0], proj.shape[1], dtype=torch.long, device=proj.device))
            projections.append(proj)
            modality_ids.append(1)
            
        if features.text is not None:
            batch_size = features.text.shape[0] if batch_size is None else batch_size
            proj = self.text_proj(features.text)
            proj = proj + self.modality_embeddings(torch.full((proj.shape[0], proj.shape[1]), 2, dtype=torch.long, device=proj.device))
            projections.append(proj)
            modality_ids.append(2)
            
        if features.temporal is not None:
            batch_size = features.temporal.shape[0] if batch_size is None else batch_size
            proj = self.temporal_proj(features.temporal)
            proj = proj + self.modality_embeddings(torch.full((proj.shape[0], proj.shape[1]), 3, dtype=torch.long, device=proj.device))
            projections.append(proj)
            modality_ids.append(3)
        
        if not projections:
            raise ValueError("No modalities provided")
        
        # Align sequence lengths
        target_len = max(p.shape[1] for p in projections)
        aligned = []
        
        for proj in projections:
            if proj.shape[1] != target_len:
                proj = F.interpolate(
                    proj.transpose(1, 2),
                    size=target_len,
                    mode='linear',
                    align_corners=False
                ).transpose(1, 2)
            aligned.append(proj)
        
        # Concatenate along sequence dimension
        fused_seq = torch.cat(aligned, dim=1)  # (batch, total_seq, hidden)
        fused_seq = self.pos_encoding(fused_seq)
        
        # Apply transformer layers
        for layer in self.layers:
            fused_seq = layer(fused_seq)
        
        # Global average pooling over sequence
        output = fused_seq.mean(dim=1)
        
        return output


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding."""
    
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        
        self.register_buffer('pe', pe)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.pe[:x.size(1), :].transpose(0, 1)
        return self.dropout(x)


class TransformerLayer(nn.Module):
    """Single transformer layer with self-attention and feedforward."""
    
    def __init__(self, dim: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        self.attention = CrossModalAttention(dim, num_heads, dropout)
        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)
        
        self.ffn = nn.Sequential(
            nn.Linear(dim, dim * 4),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(dim * 4, dim),
            nn.Dropout(dropout)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Self-attention with residual
        attn_out = self.attention(x, x, x)
        x = self.norm1(x + attn_out)
        
        # Feedforward with residual
        ffn_out = self.ffn(x)
        x = self.norm2(x + ffn_out)
        
        return x


class MultimodalClassifier(nn.Module):
    """
    Complete multimodal classification system.
    
    Combines fusion strategy with classification head.
    """
    
    def __init__(
        self,
        fusion_type: str = "attention",  # "early", "late", "attention"
        num_classes: int = 5,
        **fusion_kwargs
    ):
        super().__init__()
        
        # Select fusion strategy
        if fusion_type == "early":
            self.fusion = EarlyFusion(**fusion_kwargs)
            input_dim = fusion_kwargs.get('output_dim', 256)
        elif fusion_type == "late":
            self.fusion = LateFusion(**fusion_kwargs)
            input_dim = fusion_kwargs.get('output_dim', 256)
        elif fusion_type == "attention":
            self.fusion = AttentionFusion(**fusion_kwargs)
            input_dim = fusion_kwargs.get('hidden_dim', 256)
        else:
            raise ValueError(f"Unknown fusion type: {fusion_type}")
        
        self.fusion_type = fusion_type
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )
        
    def forward(self, features: ModalityFeatures) -> torch.Tensor:
        """
        Classify based on multimodal features.
        
        Returns:
            Class logits: (batch, num_classes)
        """
        fused = self.fusion(features)
        
        # For early/late fusion, we need to pool over sequence
        if self.fusion_type in ["early", "late"]:
            fused = fused.mean(dim=1)
        
        logits = self.classifier(fused)
        return logits


# Example usage
def example():
    """Demonstrate multimodal fusion."""
    print("=" * 60)
    print("Multimodal Fusion Engine Example")
    print("=" * 60)
    
    batch_size = 4
    seq_len = 10
    
    # Create dummy features
    features = ModalityFeatures(
        vision=torch.randn(batch_size, seq_len, 512),
        audio=torch.randn(batch_size, seq_len, 128),
        text=torch.randn(batch_size, seq_len, 768),
        temporal=torch.randn(batch_size, seq_len, 64)
    )
    
    print(f"\nInput features:")
    print(f"  Vision: {features.vision.shape}")
    print(f"  Audio: {features.audio.shape}")
    print(f"  Text: {features.text.shape}")
    print(f"  Temporal: {features.temporal.shape}")
    
    # Test Early Fusion
    print("\n1. Early Fusion:")
    early_fusion = EarlyFusion(output_dim=256)
    early_out = early_fusion(features)
    print(f"   Output: {early_out.shape}")
    
    # Test Late Fusion
    print("\n2. Late Fusion:")
    late_fusion = LateFusion(output_dim=256)
    late_out = late_fusion(features)
    print(f"   Output: {late_out.shape}")
    
    # Test Attention Fusion
    print("\n3. Attention Fusion:")
    attn_fusion = AttentionFusion(hidden_dim=256, num_heads=8, num_layers=2)
    attn_out = attn_fusion(features)
    print(f"   Output: {attn_out.shape}")
    
    # Test complete classifier
    print("\n4. Multimodal Classifier (Attention-based):")
    classifier = MultimodalClassifier(
        fusion_type="attention",
        num_classes=5,
        hidden_dim=256,
        num_heads=8,
        num_layers=2
    )
    logits = classifier(features)
    print(f"   Logits: {logits.shape}")
    print(f"   Predicted classes: {logits.argmax(dim=1)}")
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    example()
