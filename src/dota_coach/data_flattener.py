# DotA Coach Data Flattener Module
# Processes raw match JSON data into ML-ready CSV/Parquet format
# Extracts hero picks, lane matchups, skills, items, and performance metrics

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from .config import Config


class DataFlattener:
    """Flattens raw match data into ML-ready format."""
    
    def __init__(self, config: Config):
        """
        Initialize data flattener.
        
        Args:
            config (Config): Configuration manager instance.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.processed_dir = Path(config.data_dirs['processed'])
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Hero pool for filtering
        self.hero_pool = config.hero_pool
    
    def extract_match_features(self, match_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract key features from a single match.
        
        Args:
            match_data (Dict[str, Any]): Raw match data.
            
        Returns:
            Optional[Dict[str, Any]]: Extracted features, or None if invalid.
        """
        try:
            match = match_data.get('match_data', match_data)
            
            # Basic match info
            features = {
                'match_id': match.get('match_id'),
                'patch_id': match_data.get('patch_id', match.get('patch')),
                'duration': match.get('duration'),
                'radiant_win': match.get('radiant_win'),
                'game_mode': match.get('game_mode'),
                'start_time': match.get('start_time'),
            }
            
            # Extract player features for heroes in our pool
            players = match.get('players', [])
            support_players = []
            
            for player in players:
                hero_name = self._get_hero_name_from_id(player.get('hero_id'))
                if hero_name and hero_name in self.hero_pool:
                    support_players.append({
                        'hero_name': hero_name,
                        'is_radiant': player.get('isRadiant', False),
                        'lane': player.get('lane'),
                        'lane_role': player.get('lane_role'),
                        'kills': player.get('kills', 0),
                        'deaths': player.get('deaths', 0),
                        'assists': player.get('assists', 0),
                        'gold_per_min': player.get('gold_per_min', 0),
                        'xp_per_min': player.get('xp_per_min', 0),
                        'last_hits': player.get('last_hits', 0),
                        'denies': player.get('denies', 0),
                        'win': player.get('win', False),
                        'starting_items': self._extract_starting_items(player),
                        'final_items': self._extract_final_items(player),
                        'ability_upgrades': self._extract_ability_upgrades(player),
                        'first_skill': self._extract_first_skill(player),
                    })
            
            # Only process matches with at least one support from our pool
            if not support_players:
                return None
            
            # Add support player data to features
            features['support_players'] = support_players
            features['num_support_players'] = len(support_players)
            
            # Extract lane matchups for supports
            features['lane_matchups'] = self._extract_lane_matchups(players, support_players)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting features from match: {e}")
            return None
    
    def _get_hero_name_from_id(self, hero_id: int) -> Optional[str]:
        """
        Convert hero ID to hero name.
        
        Args:
            hero_id (int): Hero ID from match data.
            
        Returns:
            Optional[str]: Hero name, or None if not found.
        """
        # This would need to be implemented with constants data
        # For now, return a placeholder mapping
        hero_id_map = {
            20: 'vengeful_spirit',
            30: 'witch_doctor',
            31: 'lich',
            26: 'lion',
            85: 'undying',
            28: 'shadow_shaman',
        }
        return hero_id_map.get(hero_id)
    
    def _extract_starting_items(self, player: Dict[str, Any]) -> List[int]:
        """
        Extract starting items (first few purchases) for a player.
        
        Args:
            player (Dict[str, Any]): Player data.
            
        Returns:
            List[int]: List of starting item IDs.
        """
        purchase_log = player.get('purchase_log', [])
        
        # Get items purchased in first 60 seconds
        starting_items = []
        for purchase in purchase_log:
            if purchase.get('time', 0) <= 60:
                starting_items.append(purchase.get('key'))
        
        return starting_items[:6]  # Limit to first 6 items
    
    def _extract_final_items(self, player: Dict[str, Any]) -> List[int]:
        """
        Extract final items from player inventory.
        
        Args:
            player (Dict[str, Any]): Player data.
            
        Returns:
            List[int]: List of final item IDs.
        """
        final_items = []
        for i in range(6):  # 6 inventory slots
            item_key = f'item_{i}'
            if item_key in player:
                final_items.append(player[item_key])
        
        return final_items
    
    def _extract_ability_upgrades(self, player: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract ability upgrade order for a player.
        
        Args:
            player (Dict[str, Any]): Player data.
            
        Returns:
            List[Dict[str, Any]]: Ability upgrade sequence.
        """
        ability_upgrades = player.get('ability_upgrades_arr', [])
        
        # Convert to simpler format
        upgrades = []
        for upgrade in ability_upgrades:
            upgrades.append({
                'ability': upgrade.get('ability'),
                'time': upgrade.get('time'),
                'level': upgrade.get('level')
            })
        
        return upgrades
    
    def _extract_first_skill(self, player: Dict[str, Any]) -> Optional[int]:
        """
        Extract the first skill leveled by a player.
        
        Args:
            player (Dict[str, Any]): Player data.
            
        Returns:
            Optional[int]: First skill ID, or None if not found.
        """
        ability_upgrades = player.get('ability_upgrades_arr', [])
        
        if ability_upgrades:
            first_upgrade = min(ability_upgrades, key=lambda x: x.get('time', 0))
            return first_upgrade.get('ability')
        
        return None
    
    def _extract_lane_matchups(self, all_players: List[Dict[str, Any]], support_players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract lane matchup information for support players.
        
        Args:
            all_players (List[Dict[str, Any]]): All players in the match.
            support_players (List[Dict[str, Any]]): Support players from our hero pool.
            
        Returns:
            List[Dict[str, Any]]: Lane matchup data.
        """
        matchups = []
        
        for support in support_players:
            support_lane = support.get('lane')
            support_is_radiant = support.get('is_radiant')
            
            # Find opponents in the same lane
            opponents = []
            for player in all_players:
                if (player.get('lane') == support_lane and 
                    player.get('isRadiant') != support_is_radiant):
                    opponents.append({
                        'hero_id': player.get('hero_id'),
                        'hero_name': self._get_hero_name_from_id(player.get('hero_id')),
                        'lane_role': player.get('lane_role')
                    })
            
            matchups.append({
                'support_hero': support.get('hero_name'),
                'lane': support_lane,
                'opponents': opponents,
                'matchup_result': support.get('win')
            })
        
        return matchups
    
    def process_matches(self, match_files: List[str]) -> pd.DataFrame:
        """
        Process multiple match files into a single DataFrame.
        
        Args:
            match_files (List[str]): List of match file paths.
            
        Returns:
            pd.DataFrame: Processed match data.
        """
        all_features = []
        
        for file_path in match_files:
            try:
                with open(file_path, 'r') as f:
                    match_data = json.load(f)
                
                features = self.extract_match_features(match_data)
                if features:
                    all_features.append(features)
                    
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
        
        if not all_features:
            return pd.DataFrame()
        
        # Flatten the features into a tabular format
        flattened_data = []
        
        for match_features in all_features:
            for support_player in match_features['support_players']:
                row = {
                    'match_id': match_features['match_id'],
                    'patch_id': match_features['patch_id'],
                    'duration': match_features['duration'],
                    'radiant_win': match_features['radiant_win'],
                    'game_mode': match_features['game_mode'],
                    'hero_name': support_player['hero_name'],
                    'is_radiant': support_player['is_radiant'],
                    'lane': support_player['lane'],
                    'lane_role': support_player['lane_role'],
                    'kills': support_player['kills'],
                    'deaths': support_player['deaths'],
                    'assists': support_player['assists'],
                    'gold_per_min': support_player['gold_per_min'],
                    'xp_per_min': support_player['xp_per_min'],
                    'last_hits': support_player['last_hits'],
                    'denies': support_player['denies'],
                    'win': support_player['win'],
                    'first_skill': support_player['first_skill'],
                    'starting_items': json.dumps(support_player['starting_items']),
                    'final_items': json.dumps(support_player['final_items']),
                    'ability_upgrades': json.dumps(support_player['ability_upgrades']),
                }
                
                flattened_data.append(row)
        
        return pd.DataFrame(flattened_data)
    
    def save_processed_data(self, df: pd.DataFrame, filename: str, format: str = 'parquet') -> str:
        """
        Save processed DataFrame to disk.
        
        Args:
            df (pd.DataFrame): Processed data.
            filename (str): Output filename (without extension).
            format (str): Output format ('parquet' or 'csv').
            
        Returns:
            str: Path to saved file.
        """
        if format == 'parquet':
            filepath = self.processed_dir / f"{filename}.parquet"
            df.to_parquet(filepath, index=False)
        elif format == 'csv':
            filepath = self.processed_dir / f"{filename}.csv"
            df.to_csv(filepath, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self.logger.info(f"Saved {len(df)} rows to {filepath}")
        return str(filepath)
    
    def process_patch_data(self, patch_id: str) -> str:
        """
        Process all match data for a specific patch.
        
        Args:
            patch_id (str): Patch ID to process.
            
        Returns:
            str: Path to saved processed file.
        """
        raw_matches_dir = Path(self.config.data_dirs['raw_matches'])
        match_files = list(raw_matches_dir.glob(f"match_*_{patch_id}.json"))
        
        if not match_files:
            self.logger.warning(f"No match files found for patch {patch_id}")
            return ""
        
        # Process matches
        df = self.process_matches([str(f) for f in match_files])
        
        if df.empty:
            self.logger.warning(f"No valid data extracted for patch {patch_id}")
            return ""
        
        # Save processed data
        filename = f"processed_matches_{patch_id}"
        filepath = self.save_processed_data(df, filename, 'parquet')
        
        return filepath