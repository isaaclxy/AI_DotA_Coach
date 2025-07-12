# DotA Coach Data Loader Module
# Handles fetching match data from OpenDota API with patch filtering
# Saves raw match JSON files for later processing

import json
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import time

from .config import Config
from .explorer_query import ExplorerQuery
from .hero_mapping import HeroMapper


class DataLoader:
    """Loads and manages match data from OpenDota API."""
    
    def __init__(self, config: Config):
        """
        Initialize data loader.
        
        Args:
            config (Config): Configuration manager instance.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.raw_matches_dir = Path(config.data_dirs['raw_matches'])
        self.raw_matches_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize helper classes
        self.explorer = ExplorerQuery(config)
        self.hero_mapper = HeroMapper()
        
        # Rate limiting
        self.rate_limit = config.get('api.rate_limit_per_minute', 60)
        self.last_request_time = 0
        self.request_count = 0
        self.request_start_time = time.time()
    
    def _rate_limit_check(self) -> None:
        """Implement rate limiting for API requests."""
        current_time = time.time()
        
        # Reset counter if more than a minute has passed
        if current_time - self.request_start_time > 60:
            self.request_count = 0
            self.request_start_time = current_time
        
        # Check if we're at the rate limit
        if self.request_count >= self.rate_limit:
            sleep_time = 60 - (current_time - self.request_start_time)
            if sleep_time > 0:
                self.logger.info(f"Rate limit reached, sleeping for {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
                self.request_count = 0
                self.request_start_time = time.time()
        
        self.request_count += 1
    
    def fetch_public_matches(self, mmr_bucket: int = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch public matches from OpenDota API.
        
        Args:
            mmr_bucket (int, optional): MMR bucket for filtering matches.
            limit (int): Maximum number of matches to fetch.
            
        Returns:
            List[Dict[str, Any]]: List of match data.
        """
        self._rate_limit_check()
        
        base_url = self.config.api_base_url
        url = f"{base_url}/publicMatches"
        
        params = {}
        if mmr_bucket:
            params['mmr_bucket'] = mmr_bucket
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            matches = response.json()
            self.logger.info(f"Fetched {len(matches)} public matches")
            
            return matches[:limit]
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch public matches: {e}")
            return []
    
    def fetch_match_details(self, match_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed match data for a specific match.
        
        Args:
            match_id (int): Match ID to fetch details for.
            
        Returns:
            Optional[Dict[str, Any]]: Match details, or None if failed.
        """
        self._rate_limit_check()
        
        base_url = self.config.api_base_url
        url = f"{base_url}/matches/{match_id}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            match_data = response.json()
            self.logger.debug(f"Fetched details for match {match_id}")
            
            return match_data
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch match {match_id}: {e}")
            return None
    
    def filter_matches_by_heroes(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter matches to only include those with heroes from our pool.
        
        Args:
            matches (List[Dict[str, Any]]): List of match data.
            
        Returns:
            List[Dict[str, Any]]: Filtered matches.
        """
        hero_pool = self.config.hero_pool
        if not hero_pool:
            return matches
        
        filtered_matches = []
        
        for match in matches:
            # Check if any player in the match is playing a hero from our pool
            if 'players' in match:
                for player in match['players']:
                    hero_name = player.get('hero_name', '').lower()
                    if any(hero.lower() in hero_name for hero in hero_pool):
                        filtered_matches.append(match)
                        break
            
            # For public matches, check radiant/dire picks
            elif 'radiant_team' in match or 'dire_team' in match:
                # This is a simplified check - would need hero ID mapping
                filtered_matches.append(match)
        
        self.logger.info(f"Filtered {len(filtered_matches)} matches from {len(matches)} total")
        return filtered_matches
    
    def save_match_data(self, match_data: Dict[str, Any], patch_id: str = None) -> str:
        """
        Save match data to disk with patch-specific directory structure.
        
        Args:
            match_data (Dict[str, Any]): Match data to save.
            patch_id (str, optional): Patch ID for tagging.
            
        Returns:
            str: Path to saved file.
        """
        match_id = match_data.get('match_id')
        if not match_id:
            raise ValueError("Match data missing match_id")
        
        # Extract patch ID if not provided
        if patch_id is None:
            patch_id = match_data.get('patch', 'unknown')
        
        # Create patch-specific directory
        patch_dir = self.raw_matches_dir / f"patch_{patch_id}"
        patch_dir.mkdir(parents=True, exist_ok=True)
        
        # Add metadata
        match_with_metadata = {
            'patch_id': patch_id,
            'saved_at': datetime.now(timezone.utc).isoformat(),
            'match_data': match_data
        }
        
        # Save to patch-specific directory
        filename = f"match_{match_id}.json"
        filepath = patch_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(match_with_metadata, f, indent=2)
        
        self.logger.debug(f"Saved match data: {filepath}")
        return str(filepath)
    
    def load_saved_matches(self, patch_id: str = None) -> List[Dict[str, Any]]:
        """
        Load previously saved match data from disk.
        
        Args:
            patch_id (str, optional): Filter by specific patch ID.
            
        Returns:
            List[Dict[str, Any]]: List of loaded match data.
        """
        pattern = f"match_*_{patch_id}.json" if patch_id else "match_*.json"
        match_files = list(self.raw_matches_dir.glob(pattern))
        
        matches = []
        for filepath in match_files:
            try:
                with open(filepath, 'r') as f:
                    match_with_metadata = json.load(f)
                    matches.append(match_with_metadata)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                self.logger.error(f"Failed to load {filepath}: {e}")
        
        self.logger.info(f"Loaded {len(matches)} saved matches")
        return matches
    
    def collect_matches_for_patch(self, patch_id: str, max_matches: int = 1000) -> int:
        """
        Collect and save matches for a specific patch.
        
        Args:
            patch_id (str): Patch ID to collect matches for.
            max_matches (int): Maximum number of matches to collect.
            
        Returns:
            int: Number of matches successfully collected.
        """
        collected = 0
        
        try:
            # Fetch public matches
            public_matches = self.fetch_public_matches(limit=max_matches)
            
            # Filter for hero pool
            filtered_matches = self.filter_matches_by_heroes(public_matches)
            
            # Collect detailed match data
            for match in filtered_matches[:max_matches]:
                match_id = match.get('match_id')
                if not match_id:
                    continue
                
                # Fetch detailed match data
                detailed_match = self.fetch_match_details(match_id)
                if detailed_match:
                    # Save to disk
                    self.save_match_data(detailed_match, patch_id)
                    collected += 1
                    
                    if collected >= max_matches:
                        break
            
            self.logger.info(f"Collected {collected} matches for patch {patch_id}")
            return collected
            
        except Exception as e:
            self.logger.error(f"Failed to collect matches for patch {patch_id}: {e}")
            return collected
    
    def fetch_matches_via_explorer(self, patch_id: str, hero_ids: List[int], limit: int = 100) -> int:
        """
        Fetch matches using Explorer API with precise filtering.
        
        Args:
            patch_id (str): Exact patch ID to filter by.
            hero_ids (List[int]): List of hero IDs to include.
            limit (int): Maximum number of matches to fetch.
            
        Returns:
            int: Number of matches successfully collected.
        """
        if not hero_ids:
            self.logger.warning("No hero IDs provided")
            return 0
        
        collected = 0
        batch_size = self.config.get('explorer.batch_size', 200)
        
        try:
            self.logger.info(f"Fetching matches for patch {patch_id} with {len(hero_ids)} heroes")
            
            # Get match IDs using Explorer API
            match_ids = self.explorer.get_match_ids(patch_id, hero_ids, min(limit, batch_size))
            
            if not match_ids:
                self.logger.warning("No match IDs returned from Explorer query")
                return 0
            
            self.logger.info(f"Explorer returned {len(match_ids)} match IDs, fetching details...")
            
            # Fetch detailed match data for each ID
            for i, match_id in enumerate(match_ids[:limit]):
                try:
                    # Rate limiting
                    self._rate_limit_check()
                    
                    # Fetch match details
                    match_data = self.fetch_match_details(match_id)
                    if match_data:
                        # Save to patch-specific directory
                        self.save_match_data(match_data, patch_id)
                        collected += 1
                        
                        # Progress logging
                        if (i + 1) % 10 == 0:
                            self.logger.info(f"Fetched {i + 1}/{len(match_ids)} matches")
                    
                    # Stop if we've reached the limit
                    if collected >= limit:
                        break
                        
                except Exception as e:
                    self.logger.error(f"Failed to fetch match {match_id}: {e}")
                    continue
            
            self.logger.info(f"Successfully collected {collected} matches for patch {patch_id}")
            return collected
            
        except Exception as e:
            self.logger.error(f"Failed to fetch matches via Explorer for patch {patch_id}: {e}")
            return collected
    
    def fetch_matches_from_hero_names(self, patch_id: str, hero_names: List[str], limit: int = 100) -> int:
        """
        Fetch matches using hero names (convenience method).
        
        Args:
            patch_id (str): Exact patch ID to filter by.
            hero_names (List[str]): List of hero names to include.
            limit (int): Maximum number of matches to fetch.
            
        Returns:
            int: Number of matches successfully collected.
        """
        # Convert hero names to IDs
        hero_ids = self.hero_mapper.names_to_ids(hero_names)
        
        if not hero_ids:
            self.logger.error(f"No valid hero IDs found for names: {hero_names}")
            return 0
        
        self.logger.info(f"Converted {len(hero_names)} hero names to {len(hero_ids)} IDs")
        return self.fetch_matches_via_explorer(patch_id, hero_ids, limit)