"""
TAUI Configuration Management
Centralized configuration for all modules.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
import json
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DataConfig:
    """Data processing configuration."""
    raw_dir: Path = Path("data/raw")
    interim_dir: Path = Path("data/interim")
    processed_dir: Path = Path("data/processed")
    peer_countries: list = None

    def __post_init__(self):
        if self.peer_countries is None:
            self.peer_countries = ['TWN', 'SGP', 'KOR', 'JPN', 'HKG']
        # Create directories if they don't exist
        for dir_path in [self.raw_dir, self.interim_dir, self.processed_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

@dataclass
class PrivacyConfig:
    """Privacy filtering configuration."""
    min_conversations: int = 15
    min_users: int = 5
    suppress_small_cells: bool = True
    anonymize_output: bool = True

@dataclass
class ModelConfig:
    """Model configuration for classification."""
    task_model: str = "mock"
    mode_model: str = "mock"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000

    def __post_init__(self):
        # Try to load API key from environment
        if self.api_key is None:
            self.api_key = os.getenv("LLM_API_KEY")

@dataclass
class VisualizationConfig:
    """Visualization configuration."""
    figure_dir: Path = Path("figures")
    figure_size: tuple = (12, 8)
    dpi: int = 300
    color_scheme: str = "husl"
    font_family: str = "Microsoft JhengHei"

    def __post_init__(self):
        self.figure_dir.mkdir(parents=True, exist_ok=True)

@dataclass
class ReportConfig:
    """Report generation configuration."""
    report_dir: Path = Path("report")
    default_language: str = "zh-TW"
    include_methodology: bool = True
    include_privacy_statement: bool = True
    include_charts: bool = True
    include_data_tables: bool = True

    def __post_init__(self):
        self.report_dir.mkdir(parents=True, exist_ok=True)

@dataclass
class APIConfig:
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    log_level: str = "info"
    cors_origins: list = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]
        # Override with environment variables
        self.host = os.getenv("API_HOST", self.host)
        self.port = int(os.getenv("API_PORT", self.port))

class Config:
    """Main configuration class."""

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            config_file: Path to configuration file (JSON or YAML)
        """
        # Set default configurations
        self.data = DataConfig()
        self.privacy = PrivacyConfig()
        self.model = ModelConfig()
        self.visualization = VisualizationConfig()
        self.report = ReportConfig()
        self.api = APIConfig()

        # Load from file if provided
        if config_file and config_file.exists():
            self.load_from_file(config_file)

        # Override with environment variables
        self.load_from_env()

    def load_from_file(self, config_file: Path):
        """Load configuration from file."""
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix == '.json':
                config_data = json.load(f)
            elif config_file.suffix in ['.yml', '.yaml']:
                config_data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported config file format: {config_file.suffix}")

        # Update configurations
        self._update_config(config_data)

    def load_from_env(self):
        """Load configuration from environment variables."""
        # Privacy settings
        if min_conv := os.getenv("MIN_CONVERSATIONS"):
            self.privacy.min_conversations = int(min_conv)
        if min_users := os.getenv("MIN_USERS"):
            self.privacy.min_users = int(min_users)

        # Model settings
        if model := os.getenv("TASK_MODEL"):
            self.model.task_model = model
        if model := os.getenv("MODE_MODEL"):
            self.model.mode_model = model

        # Visualization settings
        if dpi := os.getenv("FIGURE_DPI"):
            self.visualization.dpi = int(dpi)

        # Report settings
        if lang := os.getenv("DEFAULT_LANGUAGE"):
            self.report.default_language = lang

    def _update_config(self, config_data: Dict[str, Any]):
        """Update configuration from dictionary."""
        if 'data' in config_data:
            for key, value in config_data['data'].items():
                if hasattr(self.data, key):
                    setattr(self.data, key, value)

        if 'privacy' in config_data:
            for key, value in config_data['privacy'].items():
                if hasattr(self.privacy, key):
                    setattr(self.privacy, key, value)

        if 'model' in config_data:
            for key, value in config_data['model'].items():
                if hasattr(self.model, key):
                    setattr(self.model, key, value)

        if 'visualization' in config_data:
            for key, value in config_data['visualization'].items():
                if hasattr(self.visualization, key):
                    setattr(self.visualization, key, value)

        if 'report' in config_data:
            for key, value in config_data['report'].items():
                if hasattr(self.report, key):
                    setattr(self.report, key, value)

        if 'api' in config_data:
            for key, value in config_data['api'].items():
                if hasattr(self.api, key):
                    setattr(self.api, key, value)

    def save_to_file(self, config_file: Path):
        """Save configuration to file."""
        config_data = {
            'data': {
                'raw_dir': str(self.data.raw_dir),
                'interim_dir': str(self.data.interim_dir),
                'processed_dir': str(self.data.processed_dir),
                'peer_countries': self.data.peer_countries
            },
            'privacy': {
                'min_conversations': self.privacy.min_conversations,
                'min_users': self.privacy.min_users,
                'suppress_small_cells': self.privacy.suppress_small_cells,
                'anonymize_output': self.privacy.anonymize_output
            },
            'model': {
                'task_model': self.model.task_model,
                'mode_model': self.model.mode_model,
                'temperature': self.model.temperature,
                'max_tokens': self.model.max_tokens
            },
            'visualization': {
                'figure_dir': str(self.visualization.figure_dir),
                'figure_size': self.visualization.figure_size,
                'dpi': self.visualization.dpi,
                'color_scheme': self.visualization.color_scheme,
                'font_family': self.visualization.font_family
            },
            'report': {
                'report_dir': str(self.report.report_dir),
                'default_language': self.report.default_language,
                'include_methodology': self.report.include_methodology,
                'include_privacy_statement': self.report.include_privacy_statement,
                'include_charts': self.report.include_charts,
                'include_data_tables': self.report.include_data_tables
            },
            'api': {
                'host': self.api.host,
                'port': self.api.port,
                'workers': self.api.workers,
                'reload': self.api.reload,
                'log_level': self.api.log_level,
                'cors_origins': self.api.cors_origins
            }
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            if config_file.suffix == '.json':
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            elif config_file.suffix in ['.yml', '.yaml']:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)

# Global configuration instance
config = Config()

# Export configuration objects
__all__ = ['config', 'Config', 'DataConfig', 'PrivacyConfig', 'ModelConfig',
           'VisualizationConfig', 'ReportConfig', 'APIConfig']