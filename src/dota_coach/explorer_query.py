# DotA Coach Explorer Query Module
# Handles OpenDota Explorer API queries for efficient match ID retrieval
# Uses SQL queries to filter matches by patch, rank, and heroes

import requests
import logging
from typing import List, Dict, Any, Optional

from .config import Config


class ExplorerQuery:
    """Handles OpenDota Explorer API queries for match data."""
    
    def __init__(self, config: Config):
        """
        Initialize Explorer query handler.
        
        Args:
            config (Config): Configuration manager instance.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = config.api_base_url
    
    def get_match_ids(self, patch_id: str, hero_ids: List[int], limit: int = 100) -> List[int]:
        """
        Get match IDs using Explorer API with precise filtering.
        
        Args:
            patch_id (str): Exact patch ID to filter by.
            hero_ids (List[int]): List of hero IDs to include.
            limit (int): Maximum number of matches to return.
            
        Returns:
            List[int]: List of match IDs.
        """
        if not hero_ids:
            self.logger.warning("No hero IDs provided, returning empty list")
            return []
        
        # Build SQL query with exact patch filtering
        hero_ids_str = ','.join(map(str, hero_ids))
        min_rank_tier = self.config.get('explorer.min_rank_tier', 70)
        max_days_old = self.config.get('explorer.max_days_old', 60)
        
        sql_query = f"""
        SELECT match_id
        FROM public_matches
        WHERE patch = {patch_id}
        AND avg_rank_tier >= {min_rank_tier}
        AND hero_id IN ({hero_ids_str})
        AND start_time > extract(epoch from now() - interval '{max_days_old} days')
        LIMIT {limit}
        """
        
        try:
            self.logger.info(f"Querying Explorer API for patch {patch_id} with {len(hero_ids)} heroes")
            self.logger.debug(f"SQL Query: {sql_query.strip()}")
            
            # Make request to Explorer API
            url = f"{self.base_url}/explorer"
            params = {'sql': sql_query.strip()}
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract match IDs from rows
            match_ids = []
            if 'rows' in result:
                for row in result['rows']:
                    if row and len(row) > 0:
                        # First column should be match_id
                        match_id = row[0]
                        if isinstance(match_id, int):
                            match_ids.append(match_id)
            
            self.logger.info(f"Explorer query returned {len(match_ids)} match IDs")
            return match_ids
            
        except requests.RequestException as e:
            self.logger.error(f"Explorer API request failed: {e}")
            return []
        except (KeyError, IndexError, ValueError) as e:
            self.logger.error(f"Failed to parse Explorer API response: {e}")
            return []
    
    def validate_hero_ids(self, hero_ids: List[int]) -> List[int]:
        """
        Validate that hero IDs are valid OpenDota hero IDs.
        
        Args:
            hero_ids (List[int]): List of hero IDs to validate.
            
        Returns:
            List[int]: List of valid hero IDs.
        """
        # Basic validation - hero IDs should be positive integers
        valid_ids = []
        for hero_id in hero_ids:
            if isinstance(hero_id, int) and 1 <= hero_id <= 150:  # OpenDota hero ID range
                valid_ids.append(hero_id)
            else:
                self.logger.warning(f"Invalid hero ID: {hero_id}")
        
        return valid_ids
    
    def test_connection(self) -> bool:
        """
        Test connection to Explorer API with a simple query.
        
        Returns:
            bool: True if connection successful, False otherwise.
        """
        test_query = "SELECT match_id FROM public_matches LIMIT 1"
        
        try:
            url = f"{self.base_url}/explorer"
            params = {'sql': test_query}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            # Check if we got a valid response
            if 'rows' in result and len(result['rows']) > 0:
                self.logger.info("Explorer API connection test successful")
                return True
            else:
                self.logger.warning("Explorer API returned empty result")
                return False
                
        except Exception as e:
            self.logger.error(f"Explorer API connection test failed: {e}")
            return False


def get_match_ids(config: Config, patch_id: str, hero_ids: List[int], limit: int = 100) -> List[int]:
    """
    Convenience function to get match IDs using Explorer API.
    
    Args:
        config (Config): Configuration manager instance.
        patch_id (str): Exact patch ID to filter by.
        hero_ids (List[int]): List of hero IDs to include.
        limit (int): Maximum number of matches to return.
        
    Returns:
        List[int]: List of match IDs.
    """
    explorer = ExplorerQuery(config)
    return explorer.get_match_ids(patch_id, hero_ids, limit)