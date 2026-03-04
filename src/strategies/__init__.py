"""Strategies package for the Document Intelligence Refinery."""

from src.strategies.fast_text import FastTextStrategy
from src.strategies.layout_aware import LayoutAwareStrategy
from src.strategies.vision import VisionStrategy

__all__ = [
    "FastTextStrategy",
    "LayoutAwareStrategy",
    "VisionStrategy",
]
