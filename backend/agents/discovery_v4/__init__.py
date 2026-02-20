"""
Discovery V4 Module.

This module provides the hybrid discovery system with three modes:
- Quick: AI generates everything automatically
- Guided: AI generates + optional checkpoints
- Deep: User provides interviews, AI synthesizes
"""

from agents.discovery_v4.engine import DiscoveryEngineV4

__all__ = ["DiscoveryEngineV4"]
