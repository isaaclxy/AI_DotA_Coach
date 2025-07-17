# DotA Coach Match Data Extraction Module
# Extracts player-level data from JSON match files into topline CSV format
# Handles rank cleaning by filling missing values with match averages

import json
import csv
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd

from .config import Config


class MatchDataExtractor:
    """Extracts player-level match data from JSON files to CSV format."""
    
    def __init__(self, config: Config):
        """
        Initialize match data extractor.
        
        Args:
            config (Config): Configuration manager instance.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Set up paths
        self.public_matches_dir = Path(config.data_dirs['raw_matches']).parent / "public_matches"
        self.competitive_matches_dir = Path(config.data_dirs['raw_matches'])
        self.output_path = Path(config.data_dirs['tracking']) / "match_topline_data.csv"
        
        # Statistics tracking
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'valid_matches': 0,
            'invalid_matches': 0,
            'total_players': 0,
            'players_with_original_rank': 0,
            'players_with_cleaned_rank': 0,
            'start_time': None,
            'last_progress_time': None
        }
    
    def extract_all_match_data(self) -> Dict[str, Any]:
        """
        Extract data from all match files and save to CSV.
        
        Returns:
            Dict[str, Any]: Extraction summary statistics.
        """
        self.logger.info("Starting match data extraction...")
        self.stats['start_time'] = time.time()
        self.stats['last_progress_time'] = time.time()
        
        # Collect all match files
        match_files = []
        
        # Public matches
        if self.public_matches_dir.exists():
            public_files = [(f, "public_matches") for f in self.public_matches_dir.glob("*.json")]
            match_files.extend(public_files)
        
        # Competitive matches
        if self.competitive_matches_dir.exists():
            comp_files = [(f, "matches") for f in self.competitive_matches_dir.glob("*.json")]
            match_files.extend(comp_files)
        
        self.stats['total_files'] = len(match_files)
        print(f"📊 Extracting match topline data...")
        print(f"Found {self.stats['total_files']} files to process...")
        
        # Process files and collect data
        all_player_data = []
        
        for file_path, source in match_files:
            player_data = self._process_match_file(file_path, source)
            if player_data:
                all_player_data.extend(player_data)
                self.stats['valid_matches'] += 1
            else:
                self.stats['invalid_matches'] += 1
            
            self.stats['processed_files'] += 1
            self._update_progress()
        
        # Save to CSV
        self._save_to_csv(all_player_data)
        
        # Final statistics
        elapsed = time.time() - self.stats['start_time']
        print(f"✅ Complete! Processed {self.stats['total_files']} files in {elapsed:.1f} seconds")
        print(f"- Valid matches: {self.stats['valid_matches']}")
        print(f"- Invalid/skipped: {self.stats['invalid_matches']}")
        print(f"- Total player records: {self.stats['total_players']}")
        print(f"- Players with original rank: {self.stats['players_with_original_rank']}")
        print(f"- Players with cleaned rank: {self.stats['players_with_cleaned_rank']}")
        
        return self.stats
    
    def _process_match_file(self, file_path: Path, source: str) -> Optional[List[Dict[str, Any]]]:
        """
        Process a single match file and extract player data.
        
        Args:
            file_path (Path): Path to match JSON file.
            source (str): Source type ("public_matches" or "matches").
            
        Returns:
            Optional[List[Dict[str, Any]]]: List of player records or None if invalid.
        """
        try:
            # Load JSON file
            with open(file_path, 'r') as f:
                match_data = json.load(f)
            
            # Validate match data
            if not self._validate_match_data(match_data):
                self.logger.warning(f"Invalid match data in {file_path}")
                return None
            
            # Extract basic match info
            match_info = {
                'match_id': match_data.get('match_id'),
                'patch': match_data.get('patch'),
                'start_time': match_data.get('start_time'),
                'lobby_type': match_data.get('lobby_type'),
                'source': source
            }
            
            # Process players with rank cleaning
            players = match_data.get('players', [])
            player_records = self._process_players_with_rank_cleaning(players, match_info)
            
            self.stats['total_players'] += len(player_records)
            return player_records
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            return None
    
    def _validate_match_data(self, match_data: Dict[str, Any]) -> bool:
        """
        Validate that match data has required fields.
        
        Args:
            match_data (Dict[str, Any]): Match data to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        required_fields = ['match_id', 'patch', 'start_time', 'players']
        
        for field in required_fields:
            if field not in match_data:
                return False
        
        # Check players array
        players = match_data.get('players', [])
        if not isinstance(players, list) or len(players) != 10:
            return False
        
        # Check each player has required fields
        for player in players:
            if not isinstance(player, dict):
                return False
            if 'hero_id' not in player or 'account_id' not in player:
                return False
        
        return True
    
    def _process_players_with_rank_cleaning(self, players: List[Dict[str, Any]], 
                                          match_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process players with rank cleaning logic.
        
        Args:
            players (List[Dict[str, Any]]): List of player data.
            match_info (Dict[str, Any]): Match metadata.
            
        Returns:
            List[Dict[str, Any]]: List of processed player records.
        """
        # Extract all rank tiers (excluding nulls)
        valid_ranks = []
        for player in players:
            rank = player.get('rank_tier')
            if rank is not None and rank > 0:
                valid_ranks.append(rank)
        
        # Calculate average rank for cleaning
        avg_rank = sum(valid_ranks) / len(valid_ranks) if valid_ranks else None
        
        # Process each player
        player_records = []
        for player in players:
            original_rank = player.get('rank_tier')
            
            # Determine cleaned rank
            if original_rank is not None and original_rank > 0:
                cleaned_rank = original_rank
                self.stats['players_with_original_rank'] += 1
            elif avg_rank is not None:
                cleaned_rank = round(avg_rank)  # Round to nearest integer
                self.stats['players_with_cleaned_rank'] += 1
            else:
                cleaned_rank = None
            
            # Create player record
            record = {
                'match_id': match_info['match_id'],
                'account_id': player.get('account_id'),
                'hero_id': player.get('hero_id'),
                'player_rank_tier': original_rank,
                'player_rank_tier_cleaned': cleaned_rank,
                'lobby_type': match_info['lobby_type'],
                'patch': match_info['patch'],
                'start_time': match_info['start_time'],
                'source': match_info['source']
            }
            
            player_records.append(record)
        
        return player_records
    
    def _save_to_csv(self, player_data: List[Dict[str, Any]]) -> None:
        """
        Save player data to CSV file.
        
        Args:
            player_data (List[Dict[str, Any]]): List of player records.
        """
        if not player_data:
            self.logger.warning("No data to save")
            return
        
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Define CSV columns
        columns = [
            'match_id', 'account_id', 'hero_id', 'player_rank_tier', 
            'player_rank_tier_cleaned', 'lobby_type', 'patch', 'start_time', 'source'
        ]
        
        # Write to CSV
        with open(self.output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            writer.writerows(player_data)
        
        self.logger.info(f"Saved {len(player_data)} player records to {self.output_path}")
    
    def _update_progress(self) -> None:
        """Update progress display every 5 seconds."""
        current_time = time.time()
        
        # Only update every 5 seconds
        if current_time - self.stats['last_progress_time'] < 5:
            return
        
        self.stats['last_progress_time'] = current_time
        
        # Calculate progress
        progress_pct = (self.stats['processed_files'] / self.stats['total_files']) * 100
        elapsed = current_time - self.stats['start_time']
        
        # Estimate remaining time
        if self.stats['processed_files'] > 0:
            time_per_file = elapsed / self.stats['processed_files']
            remaining_files = self.stats['total_files'] - self.stats['processed_files']
            estimated_remaining = time_per_file * remaining_files
            
            print(f"Processed {self.stats['processed_files']}/{self.stats['total_files']} files "
                  f"({progress_pct:.0f}%)... ~{estimated_remaining:.0f} seconds remaining")
        else:
            print(f"Processed {self.stats['processed_files']}/{self.stats['total_files']} files "
                  f"({progress_pct:.0f}%)...")


def extract_match_topline_data(config: Config = None) -> Dict[str, Any]:
    """
    Extract match topline data from all JSON files.
    
    Args:
        config (Config, optional): Configuration instance.
        
    Returns:
        Dict[str, Any]: Extraction summary statistics.
    """
    if config is None:
        config = Config()
    
    extractor = MatchDataExtractor(config)
    return extractor.extract_all_match_data()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run extraction
    stats = extract_match_topline_data()
    print(f"Extraction complete: {stats}")