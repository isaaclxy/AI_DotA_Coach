# DotA Coach Hero Mapping Module
# Maps hero names to OpenDota hero IDs and vice versa
# Provides conversion utilities for Explorer queries and data processing

from typing import Dict, List, Optional
import logging


class HeroMapper:
    """Maps between hero names and OpenDota hero IDs."""
    
    # OpenDota hero ID mapping for our hero pool
    HERO_NAME_TO_ID = {
        'vengeful_spirit': 20,
        'witch_doctor': 30,
        'lich': 31,
        'lion': 26,
        'undying': 85,
        'shadow_shaman': 28,
    }
    
    # Reverse mapping for ID to name lookup
    HERO_ID_TO_NAME = {v: k for k, v in HERO_NAME_TO_ID.items()}
    
    # Display names for better UX
    HERO_DISPLAY_NAMES = {
        'vengeful_spirit': 'Vengeful Spirit',
        'witch_doctor': 'Witch Doctor',
        'lich': 'Lich',
        'lion': 'Lion',
        'undying': 'Undying',
        'shadow_shaman': 'Shadow Shaman',
    }
    
    def __init__(self):
        """Initialize hero mapper."""
        self.logger = logging.getLogger(__name__)
    
    def name_to_id(self, hero_name: str) -> Optional[int]:
        """
        Convert hero name to OpenDota hero ID.
        
        Args:
            hero_name (str): Hero name (e.g., 'vengeful_spirit').
            
        Returns:
            Optional[int]: Hero ID, or None if not found.
        """
        hero_id = self.HERO_NAME_TO_ID.get(hero_name.lower())
        if hero_id is None:
            self.logger.warning(f"Unknown hero name: {hero_name}")
        return hero_id
    
    def id_to_name(self, hero_id: int) -> Optional[str]:
        """
        Convert OpenDota hero ID to hero name.
        
        Args:
            hero_id (int): OpenDota hero ID.
            
        Returns:
            Optional[str]: Hero name, or None if not found.
        """
        hero_name = self.HERO_ID_TO_NAME.get(hero_id)
        if hero_name is None:
            self.logger.warning(f"Unknown hero ID: {hero_id}")
        return hero_name
    
    def names_to_ids(self, hero_names: List[str]) -> List[int]:
        """
        Convert list of hero names to hero IDs.
        
        Args:
            hero_names (List[str]): List of hero names.
            
        Returns:
            List[int]: List of valid hero IDs (invalid names skipped).
        """
        hero_ids = []
        for name in hero_names:
            hero_id = self.name_to_id(name)
            if hero_id is not None:
                hero_ids.append(hero_id)
        
        self.logger.info(f"Converted {len(hero_names)} names to {len(hero_ids)} valid IDs")
        return hero_ids
    
    def ids_to_names(self, hero_ids: List[int]) -> List[str]:
        """
        Convert list of hero IDs to hero names.
        
        Args:
            hero_ids (List[int]): List of hero IDs.
            
        Returns:
            List[str]: List of valid hero names (invalid IDs skipped).
        """
        hero_names = []
        for hero_id in hero_ids:
            hero_name = self.id_to_name(hero_id)
            if hero_name is not None:
                hero_names.append(hero_name)
        
        return hero_names
    
    def get_display_name(self, hero_name: str) -> str:
        """
        Get display-friendly hero name.
        
        Args:
            hero_name (str): Internal hero name.
            
        Returns:
            str: Display name or original name if not found.
        """
        return self.HERO_DISPLAY_NAMES.get(hero_name.lower(), hero_name.replace('_', ' ').title())
    
    def get_all_hero_names(self) -> List[str]:
        """
        Get all supported hero names.
        
        Returns:
            List[str]: List of all hero names in the pool.
        """
        return list(self.HERO_NAME_TO_ID.keys())
    
    def get_all_hero_ids(self) -> List[int]:
        """
        Get all supported hero IDs.
        
        Returns:
            List[int]: List of all hero IDs in the pool.
        """
        return list(self.HERO_NAME_TO_ID.values())
    
    def is_valid_hero_name(self, hero_name: str) -> bool:
        """
        Check if hero name is in our supported pool.
        
        Args:
            hero_name (str): Hero name to check.
            
        Returns:
            bool: True if hero is supported, False otherwise.
        """
        return hero_name.lower() in self.HERO_NAME_TO_ID
    
    def is_valid_hero_id(self, hero_id: int) -> bool:
        """
        Check if hero ID is in our supported pool.
        
        Args:
            hero_id (int): Hero ID to check.
            
        Returns:
            bool: True if hero is supported, False otherwise.
        """
        return hero_id in self.HERO_ID_TO_NAME
    
    def parse_hero_input(self, hero_input: str) -> List[int]:
        """
        Parse hero input string and return list of hero IDs.
        Supports comma-separated hero names or IDs.
        
        Args:
            hero_input (str): Comma-separated hero names or IDs.
            
        Returns:
            List[int]: List of valid hero IDs.
        """
        if not hero_input:
            return []
        
        hero_ids = []
        items = [item.strip() for item in hero_input.split(',')]
        
        for item in items:
            # Try parsing as integer first (hero ID)
            try:
                hero_id = int(item)
                if self.is_valid_hero_id(hero_id):
                    hero_ids.append(hero_id)
                else:
                    self.logger.warning(f"Invalid hero ID: {hero_id}")
            except ValueError:
                # Try as hero name
                hero_id = self.name_to_id(item)
                if hero_id is not None:
                    hero_ids.append(hero_id)
        
        return hero_ids


# Convenience functions for direct use
def get_hero_mapper() -> HeroMapper:
    """Get a HeroMapper instance."""
    return HeroMapper()


def hero_names_to_ids(hero_names: List[str]) -> List[int]:
    """Convert hero names to IDs using default mapper."""
    mapper = HeroMapper()
    return mapper.names_to_ids(hero_names)


def hero_ids_to_names(hero_ids: List[int]) -> List[str]:
    """Convert hero IDs to names using default mapper."""
    mapper = HeroMapper()
    return mapper.ids_to_names(hero_ids)