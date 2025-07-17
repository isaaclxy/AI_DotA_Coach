# DotA Coach Match Data Pipeline Module
# Handles daily match data collection with state tracking and API rate limiting
# Manages both competitive matches and public matches with intelligent deduplication

import csv
import json
import requests
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import time

from .config import Config
from .constants import ConstantsTracker


class MatchPipeline:
    """Daily match data collection pipeline with state management."""
    
    def __init__(self, config: Config, daily_api_limit: int = 1800, enable_hero_filtering: bool = True):
        """
        Initialize match data pipeline.
        
        Args:
            config (Config): Configuration manager instance.
            daily_api_limit (int): Maximum API calls per run (default 1800).
            enable_hero_filtering (bool): Enable hero filtering in queries (default True).
        """
        self.config = config
        self.daily_api_limit = daily_api_limit
        self.api_calls_used = 0
        self.enable_hero_filtering = enable_hero_filtering
        self.logger = logging.getLogger(__name__)
        
        # Initialize paths from config (supports external drive)
        self.tracking_dir = Path(config.data_dirs['tracking'])
        self.matches_dir = Path(config.data_dirs['raw_matches'])
        self.public_matches_dir = Path(config.data_dirs['raw_matches']).parent / "public_matches"
        
        # State tracking
        self.downloaded_matches = []  # List of dicts from CSV
        self.parse_backlog = []       # List of dicts from CSV
        
        # Constants tracker for patch info
        self.constants_tracker = ConstantsTracker(config)
        
        # Rate limiting
        self.rate_limit = config.get('api.rate_limit_per_minute', 60)
        self.last_request_time = 0
        self.request_count = 0
        self.request_start_time = time.time()
        
        # Target heroes (support pool)
        self.target_hero_ids = [20, 26, 27, 28, 30, 31, 85]  # VS, Lion, Lich, SS, WD, Undying
        
        self.logger.info(f"Initialized MatchPipeline with API limit: {daily_api_limit}")
        self.logger.info(f"Hero filtering enabled: {enable_hero_filtering}")
        self.logger.info(f"Rate limiting enabled: {self.rate_limit} requests per minute")
    
    def build_hero_filter_condition(self) -> str:
        """
        Generate hero filtering SQL condition using array concatenation.
        
        Returns:
            str: SQL condition for hero filtering, or '1=1' if disabled.
        """
        if not self.enable_hero_filtering:
            return "1=1"  # Always true - no filtering
        
        # Use optimal array concatenation && overlap pattern from research
        hero_array = '[' + ','.join(map(str, self.target_hero_ids)) + ']'
        condition = f"((radiant_team || dire_team) && ARRAY{hero_array})"
        
        self.logger.debug(f"Hero filter condition: {condition}")
        return condition
    
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
    
    def load_state(self) -> bool:
        """
        Load state from CSV files.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Load downloaded matches
            downloaded_file = self.tracking_dir / "downloaded_matches.csv"
            if downloaded_file.exists():
                with open(downloaded_file, 'r') as f:
                    reader = csv.DictReader(f)
                    self.downloaded_matches = list(reader)
                self.logger.info(f"Loaded {len(self.downloaded_matches)} downloaded matches")
            else:
                self.logger.error(f"Downloaded matches file not found: {downloaded_file}")
                return False
            
            # Load parse backlog
            backlog_file = self.tracking_dir / "parse_backlog.csv"
            if backlog_file.exists():
                with open(backlog_file, 'r') as f:
                    reader = csv.DictReader(f)
                    self.parse_backlog = list(reader)
                self.logger.info(f"Loaded {len(self.parse_backlog)} matches in backlog")
            else:
                self.logger.error(f"Parse backlog file not found: {backlog_file}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            return False
    
    def save_state(self) -> bool:
        """
        Save state to CSV files.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Save downloaded matches
            downloaded_file = self.tracking_dir / "downloaded_matches.csv"
            with open(downloaded_file, 'w', newline='') as f:
                if self.downloaded_matches:
                    fieldnames = ['match_id', 'start_time', 'source', 'downloaded_time', 'file_size', 'patch']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.downloaded_matches)
                else:
                    # Write just the header if no data
                    f.write("match_id,start_time,source,downloaded_time,file_size,patch\n")
            
            # Save parse backlog
            backlog_file = self.tracking_dir / "parse_backlog.csv"
            with open(backlog_file, 'w', newline='') as f:
                if self.parse_backlog:
                    fieldnames = ['match_id', 'source', 'attempts', 'last_attempt_time', 'status', 'first_queued_time']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.parse_backlog)
                else:
                    # Write just the header if no data
                    f.write("match_id,source,attempts,last_attempt_time,status,first_queued_time\n")
            
            self.logger.info("Successfully saved state to CSV files")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
            return False
    
    def extract_match(self, match_id: int, source: str) -> Optional[Dict[str, Any]]:
        """
        Extract match data from OpenDota API and save to appropriate directory.
        Adapted from scripts/temp/extract_match.py
        
        Args:
            match_id (int): Match ID to extract.
            source (str): Source table - 'matches' or 'public_matches'.
            
        Returns:
            Optional[Dict[str, Any]]: Match metadata if successful, None otherwise.
        """
        # Validate source parameter
        if source not in ['matches', 'public_matches']:
            self.logger.error(f"Invalid source '{source}'. Must be 'matches' or 'public_matches'")
            return None
        
        # Set up output directory
        data_dir = self.public_matches_dir if source == 'public_matches' else self.matches_dir
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Fetch match data from API
        api_url = f"{self.config.api_base_url}/matches/{match_id}"
        
        try:
            self.logger.info(f"Fetching match {match_id} from OpenDota API...")
            self._rate_limit_check()
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            
            # Track API call
            self.api_calls_used += 1
            
            match_data = response.json()
            
            # Check if match was found
            if not match_data or 'match_id' not in match_data:
                self.logger.error(f"Match {match_id} not found - API returned empty or invalid response")
                return None
            
            # Check if match is parsed (has rich data)
            is_parsed = False
            if 'od_data' in match_data and match_data['od_data'].get('has_parsed'):
                is_parsed = True
                self.logger.info(f"Match {match_id} is parsed - has rich timeline data")
            else:
                self.logger.warning(f"Match {match_id} is NOT parsed - limited data available")
                return None  # Only save parsed matches
            
            # Save match data
            output_file = data_dir / f"{match_id}.json"
            
            with open(output_file, 'w') as f:
                json.dump(match_data, f, indent=2)
            
            # Get file size
            file_size = output_file.stat().st_size
            
            # Extract metadata
            duration_min = match_data.get('duration', 0) // 60
            patch = match_data.get('patch', 0)
            start_time = match_data.get('start_time', 0)
            
            self.logger.info(f"Successfully saved match {match_id} ({duration_min}min, patch {patch}) to {output_file}")
            
            # Return metadata for CSV tracking
            return {
                'match_id': str(match_id),
                'start_time': str(start_time),
                'source': source,
                'downloaded_time': datetime.now(timezone.utc).isoformat(),
                'file_size': str(file_size),
                'patch': str(patch)
            }
            
        except requests.exceptions.HTTPError as e:
            self.api_calls_used += 1  # Still count failed API calls
            if e.response.status_code == 404:
                self.logger.error(f"Match {match_id} not found - 404 error from API")
            else:
                self.logger.error(f"HTTP error fetching match {match_id}: {e}")
            return None
            
        except requests.exceptions.RequestException as e:
            self.api_calls_used += 1  # Still count failed API calls
            self.logger.error(f"Network error fetching match {match_id}: {e}")
            return None
            
        except json.JSONDecodeError as e:
            self.api_calls_used += 1  # Still count failed API calls
            self.logger.error(f"Invalid JSON response for match {match_id}: {e}")
            return None
            
        except Exception as e:
            self.logger.error(f"Unexpected error extracting match {match_id}: {e}")
            return None
    
    def send_parse_request(self, match_id: int) -> bool:
        """
        Send parse request for unparsed match.
        
        Args:
            match_id (int): Match ID to request parsing for.
            
        Returns:
            bool: True if request sent successfully, False otherwise.
        """
        try:
            api_url = f"{self.config.api_base_url}/request/{match_id}"
            self._rate_limit_check()
            response = requests.post(api_url, timeout=30)
            
            # Track API call
            self.api_calls_used += 1
            
            if response.status_code == 200:
                self.logger.info(f"Parse request sent for match {match_id}")
                return True
            else:
                self.logger.warning(f"Parse request failed for match {match_id}: {response.status_code}")
                return False
                
        except Exception as e:
            self.api_calls_used += 1  # Still count failed API calls
            self.logger.error(f"Error sending parse request for match {match_id}: {e}")
            return False
    
    def get_api_calls_used(self) -> int:
        """
        Get total API calls used in this run.
        
        Returns:
            int: Number of API calls used.
        """
        return self.api_calls_used
    
    def is_api_limit_reached(self) -> bool:
        """
        Check if API call limit has been reached.
        
        Returns:
            bool: True if limit reached, False otherwise.
        """
        return self.api_calls_used >= self.daily_api_limit
    
    def get_current_patch_timestamp(self) -> Optional[int]:
        """
        Get current patch timestamp for filtering.
        
        Returns:
            Optional[int]: Patch timestamp, or None if failed.
        """
        try:
            # Get current patch info from constants
            patch_info = self.constants_tracker.get_current_patch_info()
            
            if patch_info and patch_info.get('patch_date'):
                # Convert patch date to timestamp
                from datetime import datetime
                patch_date_str = patch_info['patch_date']
                # Handle format: "2025-05-22T23:36:01.602Z"
                patch_date = datetime.fromisoformat(patch_date_str.replace('Z', '+00:00'))
                timestamp = int(patch_date.timestamp())
                
                self.logger.info(f"Current patch timestamp: {timestamp} (patch {patch_info.get('patch_name')})")
                return timestamp
            else:
                self.logger.error("Could not get current patch timestamp")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting patch timestamp: {e}")
            return None
    
    def build_deduplication_list(self, earliest_time: int) -> List[int]:
        """
        Build list of match IDs to exclude from queries.
        
        Args:
            earliest_time (int): Earliest start_time to consider for downloaded matches.
            
        Returns:
            List[int]: List of match IDs to exclude.
        """
        exclude_ids = set()
        
        # Add downloaded matches with start_time >= earliest_time
        for match in self.downloaded_matches:
            try:
                start_time = int(match['start_time'])
                if start_time >= earliest_time:
                    exclude_ids.add(int(match['match_id']))
            except (ValueError, KeyError):
                continue
        
        # Add all backlog matches (regardless of time)
        for match in self.parse_backlog:
            try:
                exclude_ids.add(int(match['match_id']))
            except (ValueError, KeyError):
                continue
        
        result = list(exclude_ids)
        self.logger.info(f"Built deduplication list with {len(result)} match IDs")
        return result
    
    def query_explorer_api(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute SQL query against OpenDota Explorer API.
        
        Args:
            sql_query (str): SQL query to execute.
            
        Returns:
            List[Dict[str, Any]]: Query results as list of row dictionaries.
        """
        try:
            url = f"{self.config.api_base_url}/explorer"
            params = {'sql': sql_query.strip()}
            
            self.logger.debug(f"Explorer query: {sql_query.strip()}")
            self._rate_limit_check()
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Track API call
            self.api_calls_used += 1
            
            result = response.json()
            
            # Handle different response formats from OpenDota Explorer API
            rows = []
            if 'fields' in result and 'rows' in result:
                field_names = [field['name'] for field in result['fields']]
                for row in result['rows']:
                    if isinstance(row, dict):
                        # Row is already a dictionary - use as-is
                        rows.append(row)
                    elif isinstance(row, list) and len(row) == len(field_names):
                        # Row is an array - convert to dictionary
                        row_dict = dict(zip(field_names, row))
                        rows.append(row_dict)
                    else:
                        self.logger.warning(f"Unexpected row format: {row}")
            elif 'rows' in result:
                # Simple case - just rows without field definitions
                rows = result['rows']
            
            self.logger.info(f"Explorer query returned {len(rows)} rows")
            return rows
            
        except Exception as e:
            self.api_calls_used += 1  # Still count failed API calls
            self.logger.error(f"Explorer API query failed: {e}")
            return []
    
    def discover_new_matches(self, source: str, batch_size: int = 50) -> List[Dict[str, Any]]:
        """
        Discover new matches from specified source with hero filtering.
        
        Args:
            source (str): Source table ('public_matches' only for now).
            batch_size (int): Maximum matches to discover.
            
        Returns:
            List[Dict[str, Any]]: List of match dictionaries with match_id and start_time.
        """
        if source != 'public_matches':
            self.logger.warning(f"Source '{source}' not supported yet, only 'public_matches'")
            return []
        
        # Get current patch timestamp
        patch_timestamp = self.get_current_patch_timestamp()
        if not patch_timestamp:
            return []
        
        # Check API limit before proceeding
        if self.is_api_limit_reached():
            self.logger.warning("API limit reached, skipping new match discovery")
            return []
        
        try:
            # Step 1: Build hero filtering condition
            hero_filter_condition = self.build_hero_filter_condition()
            
            # Step 2: Get earliest start_time for deduplication
            earliest_query = f"""
            SELECT MIN(start_time)
            FROM {source}
            WHERE start_time > {patch_timestamp}
            AND avg_rank_tier >= 70
            AND lobby_type = 7
            AND game_mode = 22
            AND {hero_filter_condition}
            """
            
            earliest_result = self.query_explorer_api(earliest_query)
            if not earliest_result:
                self.logger.warning("Could not get earliest start_time from Explorer API")
                return []
            
            # Use 'min' field name since OpenDota doesn't handle aliases properly
            earliest_time_value = earliest_result[0].get('min')
            
            if earliest_time_value is None:
                self.logger.warning("No matches found in timeframe")
                return []
            
            earliest_time = int(earliest_time_value)
            self.logger.info(f"Earliest match time for deduplication: {earliest_time}")
            
            # Check API limit after first query
            if self.is_api_limit_reached():
                self.logger.warning("API limit reached after earliest time query")
                return []
            
            # Step 3: Build deduplication list
            exclude_ids = self.build_deduplication_list(earliest_time)
            
            # Step 4: Build exclusion condition
            if exclude_ids:
                exclude_list = ','.join(map(str, exclude_ids))
                exclude_condition = f"AND match_id NOT IN ({exclude_list})"
            else:
                exclude_condition = ""
            
            # Step 5: Enhanced discovery query with hero filtering
            discovery_query = f"""
            SELECT match_id, start_time
            FROM {source}
            WHERE start_time > {patch_timestamp}
            AND avg_rank_tier >= 70
            AND lobby_type = 7
            AND game_mode = 22
            AND {hero_filter_condition}
            {exclude_condition}
            ORDER BY start_time DESC
            LIMIT {batch_size}
            """
            
            matches = self.query_explorer_api(discovery_query)
            self.logger.info(f"Discovered {len(matches)} new matches from {source}")
            return matches
            
        except Exception as e:
            self.logger.error(f"Error discovering new matches from {source}: {e}")
            return []
    
    def process_backlog(self) -> int:
        """
        Process matches in parse backlog.
        
        Returns:
            int: Number of matches successfully processed from backlog.
        """
        if not self.parse_backlog:
            self.logger.info("No matches in parse backlog")
            return 0
        
        processed_count = 0
        remaining_backlog = []
        
        self.logger.info(f"Processing {len(self.parse_backlog)} matches from backlog")
        
        for backlog_entry in self.parse_backlog:
            # Check API limit
            if self.is_api_limit_reached():
                self.logger.warning("API limit reached during backlog processing")
                remaining_backlog.append(backlog_entry)
                continue
            
            try:
                match_id = int(backlog_entry['match_id'])
                source = backlog_entry['source']
                attempts = int(backlog_entry.get('attempts', 0))
                status = backlog_entry.get('status', 'pending')
                
                # Skip if already marked as skipped or too many attempts
                if status == 'skipped' or attempts >= 2:
                    self.logger.debug(f"Skipping match {match_id} (status: {status}, attempts: {attempts})")
                    remaining_backlog.append(backlog_entry)
                    continue
                
                # Try to extract the match
                match_metadata = self.extract_match(match_id, source)
                
                if match_metadata:
                    # Success! Add to downloaded matches and remove from backlog
                    self.downloaded_matches.append(match_metadata)
                    processed_count += 1
                    self.logger.info(f"Successfully processed match {match_id} from backlog")
                else:
                    # Still not parsed, increment attempts
                    backlog_entry['attempts'] = str(attempts + 1)
                    backlog_entry['last_attempt_time'] = datetime.now(timezone.utc).isoformat()
                    
                    if attempts + 1 >= 2:
                        backlog_entry['status'] = 'skipped'
                        self.logger.info(f"Marking match {match_id} as skipped after 2 attempts")
                    
                    remaining_backlog.append(backlog_entry)
                    
            except (ValueError, KeyError) as e:
                self.logger.error(f"Invalid backlog entry: {backlog_entry}, error: {e}")
                continue
        
        # Update backlog with remaining entries
        self.parse_backlog = remaining_backlog
        
        self.logger.info(f"Processed {processed_count} matches from backlog, {len(remaining_backlog)} remaining")
        return processed_count
    
    def process_new_matches(self, new_matches: List[Dict[str, Any]], source: str) -> int:
        """
        Process newly discovered matches.
        
        Args:
            new_matches (List[Dict[str, Any]]): List of match dictionaries from discovery.
            source (str): Source table name.
            
        Returns:
            int: Number of matches successfully processed.
        """
        if not new_matches:
            return 0
        
        processed_count = 0
        
        self.logger.info(f"Processing {len(new_matches)} new matches from {source}")
        
        for match_info in new_matches:
            # Check API limit
            if self.is_api_limit_reached():
                self.logger.warning("API limit reached during new match processing")
                break
            
            try:
                match_id = int(match_info['match_id'])
                start_time = int(match_info['start_time'])
                
                # Try to extract the match
                match_metadata = self.extract_match(match_id, source)
                
                if match_metadata:
                    # Success! Add to downloaded matches
                    self.downloaded_matches.append(match_metadata)
                    processed_count += 1
                    self.logger.info(f"Successfully processed new match {match_id}")
                else:
                    # Not parsed yet, send parse request and add to backlog
                    parse_sent = self.send_parse_request(match_id)
                    
                    if parse_sent or True:  # Add to backlog even if parse request fails
                        backlog_entry = {
                            'match_id': str(match_id),
                            'source': source,
                            'attempts': '1',
                            'last_attempt_time': datetime.now(timezone.utc).isoformat(),
                            'status': 'pending',
                            'first_queued_time': datetime.now(timezone.utc).isoformat()
                        }
                        self.parse_backlog.append(backlog_entry)
                        self.logger.info(f"Added match {match_id} to parse backlog")
                    
            except (ValueError, KeyError) as e:
                self.logger.error(f"Invalid match info: {match_info}, error: {e}")
                continue
        
        self.logger.info(f"Processed {processed_count} new matches from {source}")
        return processed_count
    
    def run_daily_pipeline(self, batch_size: int = 50) -> Dict[str, Any]:
        """
        Run the complete daily match data pipeline.
        
        Args:
            batch_size (int): Maximum new matches to discover per source.
            
        Returns:
            Dict[str, Any]: Summary of pipeline execution.
        """
        start_time = time.time()
        self.logger.info("Starting daily match data pipeline")
        
        # Step 0: Load state
        if not self.load_state():
            return {
                'success': False,
                'error': 'Failed to load state files',
                'api_calls_used': self.api_calls_used
            }
        
        # Step 1: Process backlog
        backlog_processed = self.process_backlog()
        
        # Step 2: Discover and process new matches (public_matches only for now)
        new_matches_processed = 0
        if not self.is_api_limit_reached():
            new_matches = self.discover_new_matches('public_matches', batch_size)
            new_matches_processed = self.process_new_matches(new_matches, 'public_matches')
        
        # Step 3: Save state
        save_success = self.save_state()
        
        # Generate summary
        end_time = time.time()
        duration = end_time - start_time
        
        summary = {
            'success': save_success,
            'duration_seconds': round(duration, 2),
            'backlog_processed': backlog_processed,
            'new_matches_processed': new_matches_processed,
            'total_matches_processed': backlog_processed + new_matches_processed,
            'api_calls_used': self.api_calls_used,
            'api_limit': self.daily_api_limit,
            'remaining_backlog': len(self.parse_backlog),
            'total_downloaded': len(self.downloaded_matches)
        }
        
        self.logger.info(f"Pipeline completed in {duration:.2f}s")
        self.logger.info(f"Processed {summary['total_matches_processed']} matches total")
        self.logger.info(f"API calls used: {self.api_calls_used}/{self.daily_api_limit}")
        
        return summary