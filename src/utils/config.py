import os
import hydra
import logging

from pathlib import Path
from omegaconf import DictConfig
from hydra.core.hydra_config import HydraConfig
from hydra import compose, initialize_config_dir

from src.helpers import logme


class ProcessingConfig:
    @staticmethod
    def get_project_root() -> Path:
        """Get the absolute path to the project root directory."""
        current_file = Path(__file__).resolve()
        return current_file.parent.parent.parent

    @staticmethod
    def setup_config() -> DictConfig:
        """Initialize Hydra with the correct config path."""
        try:
            # Get project root and config paths
            project_root = ProcessingConfig.get_project_root()
            config_dir = str(project_root / "configs")
            
            # Debug logging
            logme(f"Current working directory: {os.getcwd()}")
            logme(f"Project root path: {project_root}")
            logme(f"Config directory path: {config_dir}")
            
            # Initialize using absolute config directory path
            with initialize_config_dir(config_dir=config_dir, version_base=None):
                cfg = compose(config_name="data_processing")
            
            return cfg
            
        except Exception as e:
            logme(f"Failed to setup config: {str(e)}", level="error")
            raise


    @staticmethod
    def setup_logging(cfg: DictConfig) -> None:
        """Configure logging system with paths relative to project root
        
        Args:
            cfg: Hydra configuration object
        """
        # Get project root directory
        project_root = Path(__file__).parent.parent.parent
        
        # Create output directory if it doesn't exist
        output_dir = project_root / cfg.data.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(str(output_dir / "processing.log")),
                logging.StreamHandler()
            ]
        )