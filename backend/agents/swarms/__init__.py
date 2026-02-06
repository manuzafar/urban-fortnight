"""
Swarm Architecture for Parallel Agent Execution.

This package implements a swarm-based architecture where groups of
related agents run in parallel, coordinated by a central Facilitator.

Swarms:
- DiscoverySwarm: Market research, competitive intel, personas
- StrategySwarm: Business strategy, GTM, financial modeling
- DeliverySwarm: PRD, tech architecture, legal, risk assessment
"""

from agents.swarms.base import BaseSwarm
from agents.swarms.discovery_swarm import DiscoverySwarm
from agents.swarms.strategy_swarm import StrategySwarm
from agents.swarms.delivery_swarm import DeliverySwarm

__all__ = [
    "BaseSwarm",
    "DiscoverySwarm",
    "StrategySwarm",
    "DeliverySwarm",
]
