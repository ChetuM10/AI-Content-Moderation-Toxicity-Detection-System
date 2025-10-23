"""MongoDB document models and helper functions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId


@dataclass
class User:
    """Data class representing a user document."""

    email: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_document(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class AnalysisRecord:
    """Data class representing an analysis history document."""

    user_id: ObjectId
    original_text: str
    cleaned_text: str
    rewrite_suggestion: Optional[str] = None
    rewrite_method: Optional[str] = None
    toxicity_scores: Dict[str, float] = field(default_factory=dict)
    sentiment_original: Dict[str, Any] = field(default_factory=dict)
    sentiment_cleaned: Dict[str, Any] = field(default_factory=dict)
    categories_flagged: List[str] = field(default_factory=list)
    toxic_words_found: List[str] = field(default_factory=list)
    toxic_word_count: int = 0
    overall_toxicity: float = 0.0
    sentiment_improvement: float = 0.0
    sentiment_improved: bool = False
    is_toxic: bool = False
    source: str = "text"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    favorite: bool = False

    def to_document(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "original_text": self.original_text,
            "cleaned_text": self.cleaned_text,
            "rewrite_suggestion": self.rewrite_suggestion,
            "rewrite_method": self.rewrite_method,
            "toxicity_scores": self.toxicity_scores,
            "sentiment_original": self.sentiment_original,
            "sentiment_cleaned": self.sentiment_cleaned,
            "categories_flagged": self.categories_flagged,
            "toxic_words_found": self.toxic_words_found,
            "toxic_word_count": self.toxic_word_count,
            "overall_toxicity": self.overall_toxicity,
            "sentiment_improvement": self.sentiment_improvement,
            "sentiment_improved": self.sentiment_improved,
            "is_toxic": self.is_toxic,
            "source": self.source,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "favorite": self.favorite,
        }