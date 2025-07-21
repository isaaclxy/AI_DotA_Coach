# DotA Coach Constants Tracking Module
# Handles OpenDota constants API snapshots and patch tracking
# Provides patch-aware constants history for ML model adaptation

import json
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from .config import Config


class ConstantsTracker:
    """Tracks and manages OpenDota constants snapshots."""
    
    def __init__(self, config: Config):
        """
        Initialize constants tracker.
        
        Args:
            config (Config): Configuration manager instance.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.snapshots_dir = Path(config.data_dirs['constants'])
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_constants(self, rate_limiter_func=None) -> Dict[str, Any]:
        """
        Fetch current constants from OpenDota API.
        
        Args:
            rate_limiter_func: Optional function to call before each API request for rate limiting.
        
        Returns:
            Dict[str, Any]: Combined constants data from all endpoints.
        """
        base_url = self.config.api_base_url
        constants_data = {}
        
        for endpoint in self.config.constants_endpoints:
            try:
                # Apply rate limiting if provided
                if rate_limiter_func:
                    rate_limiter_func()
                    
                url = f"{base_url}/constants/{endpoint}"
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                constants_data[endpoint] = response.json()
                self.logger.info(f"Fetched constants for {endpoint}")
                
            except requests.RequestException as e:
                self.logger.error(f"Failed to fetch {endpoint}: {e}")
                constants_data[endpoint] = None
        
        return constants_data
    
    def get_current_patch_info(self, rate_limiter_func=None) -> Dict[str, Any]:
        """
        Fetch current patch information from OpenDota API.
        
        Args:
            rate_limiter_func: Optional function to call before API request for rate limiting.
        
        Returns:
            Dict[str, Any]: Current patch metadata including name, numeric ID, and date.
        """
        try:
            # Apply rate limiting if provided
            if rate_limiter_func:
                rate_limiter_func()
                
            self.logger.info("Fetching patch metadata from /constants/patch endpoint")
            url = f"{self.config.api_base_url}/constants/patch"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            patches = response.json()
            if not patches or not isinstance(patches, list):
                self.logger.error("No patch data found or invalid format")
                return {
                    'patch_name': 'unknown',
                    'patch_numeric_id': 0,
                    'patch_date': None
                }
            
            # Get the latest patch (highest ID or most recent date)
            latest_patch = max(patches, key=lambda p: p.get('id', 0))
            
            patch_info = {
                'patch_name': latest_patch.get('name', 'unknown'),
                'patch_numeric_id': latest_patch.get('id', 0),
                'patch_date': latest_patch.get('date')
            }
            
            self.logger.info(f"Retrieved patch info: {patch_info['patch_name']} (ID: {patch_info['patch_numeric_id']}, Date: {patch_info['patch_date']})")
            return patch_info
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch patch info: {e}")
            return {
                'patch_name': 'unknown',
                'patch_numeric_id': 0,
                'patch_date': None
            }
    
    def save_snapshot(self, constants_data: Dict[str, Any], patch_id: str = None, rate_limiter_func=None) -> str:
        """
        Save constants snapshot to disk with enhanced metadata.
        
        Args:
            constants_data (Dict[str, Any]): Constants data to save.
            patch_id (str, optional): Patch ID. If None, fetched from patch API.
            rate_limiter_func: Optional function to call before API request for rate limiting.
            
        Returns:
            str: Path to saved snapshot file.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        datetime_captured = datetime.now(timezone.utc).isoformat()
        
        # Get current patch info
        patch_info = self.get_current_patch_info(rate_limiter_func)
        
        # Use provided patch_id or fallback to fetched patch name
        if patch_id is None:
            patch_id = patch_info['patch_name']
        
        self.logger.info("Creating enhanced snapshot metadata")
        self.logger.info(f"Snapshot metadata: patch={patch_info['patch_name']}, numeric_id={patch_info['patch_numeric_id']}, captured={datetime_captured}")
        
        # Create snapshot with enhanced metadata
        snapshot = {
            'timestamp': timestamp,
            'patch_id': patch_id,  # Keep for backwards compatibility
            'patch_name': patch_info['patch_name'],
            'patch_numeric_id': patch_info['patch_numeric_id'],
            'datetime_captured': datetime_captured,
            'patch_date': patch_info['patch_date'],
            'constants': constants_data
        }
        
        # Save to file
        filename = f"constants_{patch_id}_{timestamp}.json"
        filepath = self.snapshots_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        self.logger.info(f"Saved constants snapshot: {filename}")
        return str(filepath)
    
    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent constants snapshot.
        
        Returns:
            Optional[Dict[str, Any]]: Latest snapshot data, or None if none exist.
        """
        snapshot_files = list(self.snapshots_dir.glob("constants_*.json"))
        
        if not snapshot_files:
            return None
        
        # Sort by modification time and get latest
        latest_file = max(snapshot_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    def compare_snapshots(self, snapshot1: Dict[str, Any], snapshot2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two constants snapshots and return differences.
        
        Args:
            snapshot1 (Dict[str, Any]): First snapshot (usually older).
            snapshot2 (Dict[str, Any]): Second snapshot (usually newer).
            
        Returns:
            Dict[str, Any]: Differences between snapshots.
        """
        # Normalize patch IDs to handle legacy snapshots with mixed ID types
        patch_id1 = self._normalize_patch_id(snapshot1)
        patch_id2 = self._normalize_patch_id(snapshot2)
        
        diff = {
            'patch_change': patch_id1 != patch_id2,
            'timestamp1': snapshot1.get('timestamp'),
            'timestamp2': snapshot2.get('timestamp'),
            'endpoint_changes': {}
        }
        
        constants1 = snapshot1.get('constants', {})
        constants2 = snapshot2.get('constants', {})
        
        for endpoint in self.config.constants_endpoints:
            data1 = constants1.get(endpoint)
            data2 = constants2.get(endpoint)
            
            if data1 != data2:
                diff['endpoint_changes'][endpoint] = {
                    'changed': True,
                    'details': f"Data differs between snapshots"
                }
            else:
                diff['endpoint_changes'][endpoint] = {'changed': False}
        
        return diff
    
    def update_constants(self, rate_limiter_func=None) -> str:
        """
        Fetch latest constants and save snapshot only if different from last.
        
        Args:
            rate_limiter_func: Optional function to call before each API request for rate limiting.
        
        Returns:
            str: Status message about the update.
        """
        try:
            # Fetch current constants
            current_constants = self.fetch_constants(rate_limiter_func)
            
            # Get latest snapshot for comparison
            latest_snapshot = self.get_latest_snapshot()
            
            # Always save first snapshot
            if latest_snapshot is None:
                filepath = self.save_snapshot(current_constants, rate_limiter_func=rate_limiter_func)
                return f"Saved initial constants snapshot: {filepath}"
            
            # Extract patch ID from current constants for comparison
            current_patch_id = self._extract_patch_id(current_constants)
            latest_patch_id = latest_snapshot.get('patch_id', 'unknown')
            
            # Create temp snapshot for comparison
            current_snapshot = {
                'patch_id': current_patch_id,
                'constants': current_constants,
                'timestamp': datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            }
            
            # Compare snapshots using existing logic
            diff = self.compare_snapshots(latest_snapshot, current_snapshot)
            
            # Save only if there are actual changes
            if diff['patch_change'] or any(
                change['changed'] for change in diff['endpoint_changes'].values()
            ):
                filepath = self.save_snapshot(current_constants, current_patch_id, rate_limiter_func)
                self.logger.info(f"Constants changed - saved new snapshot: {filepath}")
                return f"Saved updated constants snapshot: {filepath}"
            else:
                self.logger.info("No changes detected in constants")
                return "No changes detected, snapshot not saved"
                
        except Exception as e:
            self.logger.error(f"Failed to update constants: {e}")
            return f"Update failed: {e}"
    
    def _extract_patch_id(self, constants_data: Dict[str, Any]) -> str:
        """
        Extract current patch ID by fetching from patch API.
        
        Args:
            constants_data (Dict[str, Any]): Constants data (unused, kept for compatibility).
            
        Returns:
            str: Current patch name (e.g., '7.39') or 'unknown' if not found.
        """
        # Get current patch info from API instead of constants data
        patch_info = self.get_current_patch_info()
        return patch_info['patch_name']
    
    def _normalize_patch_id(self, snapshot: Dict[str, Any]) -> str:
        """
        Normalize patch ID from snapshot to always return patch name.
        
        Handles legacy snapshots that may have stored patch ID numbers instead of names.
        If the stored patch_id is numeric (like '58'), tries to convert it to patch name.
        
        Args:
            snapshot (Dict[str, Any]): Snapshot data.
            
        Returns:
            str: Normalized patch name (e.g., '7.39').
        """
        stored_patch_id = snapshot.get('patch_id', 'unknown')
        
        # If it's already a patch name format (contains dots), return as-is
        if '.' in str(stored_patch_id):
            return str(stored_patch_id)
        
        # If it's numeric (legacy format), try to convert to patch name
        if str(stored_patch_id).isdigit():
            constants_data = snapshot.get('constants', {})
            patch_data = constants_data.get('patch', [])
            
            if patch_data and isinstance(patch_data, list):
                # Find the patch with matching ID
                for patch in patch_data:
                    if isinstance(patch, dict) and str(patch.get('id')) == str(stored_patch_id):
                        return str(patch.get('name', 'unknown'))
        
        # Fallback to stored value if conversion fails
        return str(stored_patch_id)
    
    def get_current_patch_id(self) -> Optional[str]:
        """
        Get the current patch ID from the latest constants snapshot.
        
        Returns:
            Optional[str]: Current patch ID, or None if no snapshots exist.
        """
        latest_snapshot = self.get_latest_snapshot()
        if latest_snapshot:
            return latest_snapshot.get('patch_id')
        return None