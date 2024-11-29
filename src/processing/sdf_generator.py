import os
import logging
import subprocess

import numpy as np

from omegaconf import DictConfig
from typing import Optional, Tuple

from src.helpers import logme


class SDFGenerator:
    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        self.logger = logging.getLogger(__name__)
        self.sdfgen_path = os.path.join(cfg.processing.sdfgen_path, "sdfgen")
        
    def generate_sdf(self, mesh_path: str, output_path: str) -> Optional[np.ndarray]:
        """Generate SDF using SDFGen"""
        try:
            # Run SDFGen
            cmd = [
                self.sdfgen_path,
                mesh_path,
                str(self.cfg.data.sdf_resolution),
                output_path
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"SDFGen failed: {stderr.decode()}")
                return None
                
            # Load generated SDF
            sdf = self._load_sdf(output_path)
            
            # Convert to TSDF
            tsdf = self._convert_to_tsdf(sdf)
            
            return tsdf
            
        except Exception as e:
            self.logger.error(f"Error generating SDF: {str(e)}")
            return None
            
    def _load_sdf(self, sdf_path: str) -> np.ndarray:
        """Load SDF from file"""
        with open(sdf_path, 'rb') as f:
            # Read header
            dims = np.fromfile(f, dtype=np.int32, count=3)
            
            # Read transformation matrix
            transform = np.fromfile(f, dtype=np.float32, count=12)
            transform = transform.reshape(3, 4)
            
            # Read SDF values
            sdf = np.fromfile(f, dtype=np.float32)
            sdf = sdf.reshape(dims)
            
        return sdf
        
    def _convert_to_tsdf(self, sdf: np.ndarray) -> np.ndarray:
        """Convert SDF to TSDF"""
        truncation = self.cfg.data.tsdf_truncation
        tsdf = np.clip(sdf, -truncation, truncation)
        return tsdf