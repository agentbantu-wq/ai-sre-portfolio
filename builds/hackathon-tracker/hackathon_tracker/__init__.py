"""
Hackathon Opportunity Tracker

A comprehensive tool for discovering, analyzing, and ranking hackathon opportunities
across multiple sources to maximize earning potential and participation rewards.
"""

__version__ = "1.0.0"
__author__ = "AI SRE Portfolio"
__email__ = "portfolio@example.com"
__license__ = "MIT"

from .tracker import HackathonTracker, HackathonOpportunity

__all__ = [
    "HackathonTracker",
    "HackathonOpportunity",
]