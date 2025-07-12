# DotA Coach Configuration Module
# Configuration management for DotA Coach system
# Handles loading from config.yaml and .env files

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any
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
        """Get data directory paths."""
        return {
            'raw_matches': self.get('data.raw_matches_dir', 'data/raw/matches'),
            'processed': self.get('data.processed_data_dir', 'data/processed'),
            'constants': self.get('data.constants_snapshots_dir', 'constants/snapshots'),
            'models': self.get('data.models_dir', 'models')
        }