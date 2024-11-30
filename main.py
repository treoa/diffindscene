import os
import logging

from pathlib import Path

from src_archive.helpers import logme
from src_archive.processing import ProcessingPipeline
from src_archive.utils.config import ProcessingConfig


def main():
    try:
        # Setup configuration
        cfg = ProcessingConfig.setup_config()
        ProcessingConfig.setup_logging(cfg)
        
        # Log important paths for debugging
        project_root = Path(__file__).parent
        logme(f"Project root directory: {project_root}")
        logme(f"Config directory: {project_root / 'configs'}")
        logme(f"Imported configs: {cfg}")
        
        # Initialize and run pipeline
        pipeline = ProcessingPipeline(cfg)
        pipeline.process_dataset()
        
    except Exception as e:
        logme(f"Pipeline execution failed: {str(e)}", level="error")
        raise

if __name__ == "__main__":
    main()