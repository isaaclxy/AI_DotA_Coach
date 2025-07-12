# DotA Coach Package
# Package initialization for DotA Coach AI system
# Core module for Dota 2 coaching functionality

__version__ = "0.1.0"
__author__ = "Isaac"
__description__ = "AI-powered personal coaching system for Dota 2 players"

from .config import Config
from .constants import ConstantsTracker
from .data_loader import DataLoader
from .data_flattener import DataFlattener
from .explorer_query import ExplorerQuery
from .hero_mapping import HeroMapper

__all__ = [
    "Config",
    "ConstantsTracker", 
    "DataLoader",
    "DataFlattener",
    "ExplorerQuery",
    "HeroMapper"
]