# DotA Coach Configuration Module
# Configuration management for DotA Coach system
# Handles loading from config.yaml and .env files

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for DotA Coach system."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration manager.
        
        Args:
            config_path (str): Path to YAML configuration file.
        """
        self.config_path = Path(config_path)
        self.config_data: Dict[str, Any] = {}
        
        # Load environment variables
        load_dotenv()
        
        # Load YAML configuration
        self._load_config()
        
        # Set up logger
        self.logger = logging.getLogger(__name__)
        
        # Resolve data path (local or external)
        self._data_base_path = self._resolve_data_path()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self.config_data = yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with dot notation support.
        
        Args:
            key (str): Configuration key (supports dot notation like 'api.base_url').
            default (Any): Default value if key not found.
            
        Returns:
            Any: Configuration value.
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_env(self, key: str, default: str = None) -> str:
        """
        Get environment variable value.
        
        Args:
            key (str): Environment variable name.
            default (str): Default value if not found.
            
        Returns:
            str: Environment variable value.
        """
        return os.getenv(key, default)
    
    def _resolve_data_path(self) -> str:
        """
        Resolve data directory path - either local or external drive.
        
        Returns:
            str: Base path for data directory.
        """
        config_file = Path("data/.data_location")
        
        # If no config file, use local data directory
        if not config_file.exists():
            return "data"
        
        try:
            # Read config file and find the path
            with open(config_file, 'r') as f:
                lines = f.readlines()
            
            # Find the reference line and get the path after it
            reference_line = "# ENTER YOUR PATH BELOW THIS LINE:"
            path_line = None
            
            for i, line in enumerate(lines):
                if reference_line in line:
                    # Look for the next non-empty, non-comment line
                    for j in range(i + 1, len(lines)):
                        potential_path = lines[j].strip()
                        if potential_path and not potential_path.startswith('#'):
                            path_line = potential_path
                            break
                    break
            
            # If no path found, use local directory
            if not path_line:
                self.logger.info("Config file found but empty, using local data directory")
                return "data"
            
            # Validate and return external path
            return self._validate_external_path(path_line)
            
        except Exception as e:
            self.logger.error(f"Error reading external path config: {e}")
            raise RuntimeError(f"Failed to read external path configuration: {e}")
    
    def _validate_external_path(self, path_str: str) -> str:
        """
        Validate external path and handle Windows drive fallback.
        
        Args:
            path_str (str): Path string from config file.
            
        Returns:
            str: Validated path.
            
        Raises:
            RuntimeError: If path is invalid or inaccessible.
        """
        # Strip whitespace
        path_str = path_str.strip()
        
        # Reject relative paths
        if not os.path.isabs(path_str):
            raise RuntimeError(f"External path must be absolute, got: {path_str}")
        
        path = Path(path_str)
        
        # Try original path first
        if self._check_path_accessibility(path):
            return str(path)
        
        # Windows drive fallback
        if os.name == 'nt' and len(path_str) > 2 and path_str[1] == ':':
            original_drive = path_str[0].upper()
            path_without_drive = path_str[2:]  # Remove "D:" part
            
            # Try other drive letters
            for drive_letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                if drive_letter != original_drive:
                    fallback_path = Path(f"{drive_letter}:{path_without_drive}")
                    if self._check_path_accessibility(fallback_path):
                        self.logger.warning(f"Drive letter changed from {original_drive}: to {drive_letter}:, using {fallback_path}")
                        return str(fallback_path)
        
        # Path not found
        raise RuntimeError(f"External path not found or inaccessible: {path_str}")
    
    def _check_path_accessibility(self, path: Path) -> bool:
        """
        Check if path exists, is directory, and is writable.
        
        Args:
            path (Path): Path to check.
            
        Returns:
            bool: True if accessible.
        """
        try:
            # Check if path exists and is directory
            if not path.exists():
                return False
            if not path.is_dir():
                return False
            
            # Test write permissions
            test_file = path / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            
            # Check required subdirectories exist
            required_dirs = ['raw', 'raw/matches', 'raw/public_matches', 'processed', 'tracking']
            for subdir in required_dirs:
                subdir_path = path / subdir
                if not subdir_path.exists():
                    raise RuntimeError(f"Required subdirectory missing: {subdir_path}")
            
            # Check if directory has some data (not completely empty)
            if not any(path.iterdir()):
                raise RuntimeError(f"Directory found but empty. Please copy data directory from codebase to configured location: {path}")
            
            return True
            
        except Exception as e:
            if "Required subdirectory missing" in str(e) or "Directory found but empty" in str(e):
                raise  # Re-raise our specific errors
            return False
    
    @property
    def api_base_url(self) -> str:
        """Get OpenDota API base URL."""
        return self.get('api.base_url', 'https://api.opendota.com/api')
    
    @property
    def api_key(self) -> str:
        """Get OpenDota API key from environment."""
        return self.get_env('OPENDOTA_API_KEY', '')
    
    @property
    def hero_pool(self) -> List[str]:
        """Get configured hero pool."""
        return self.get('matches.hero_pool', [])
    
    @property
    def constants_endpoints(self) -> List[str]:
        """Get constants API endpoints to track."""
        return self.get('constants.endpoints', [])
    
    @property
    def data_dirs(self) -> Dict[str, str]:
        """Get data directory paths (local or external based on configuration)."""
        # Use resolved base path for data directories
        base_path = self._data_base_path
        
        return {
            'raw_matches': f"{base_path}/raw/matches",
            'processed': f"{base_path}/processed",
            'tracking': f"{base_path}/tracking",
            'constants': self.get('data.constants_snapshots_dir', 'constants/snapshots'),
            'models': self.get('data.models_dir', 'models')
        }