import trimesh
import logging

import numpy as np

from typing import Optional
from omegaconf import DictConfig

from src.helpers.logger import logme


class MeshProcessor:
    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        self.logger = logging.getLogger(__name__)
        
    def process_mesh(self, mesh: trimesh.Trimesh) -> Optional[trimesh.Trimesh]:
        """Process single mesh with initial cleanup"""
        try:
            # Remove duplicate vertices
            mesh = mesh.merge_vertices()
            
            # Fix mesh winding and normals
            mesh.fix_normals()
            
            # Check mesh validity
            if not mesh.is_watertight:
                self.logger.warning("Mesh is not watertight")
            
            # Scale to target size
            scale = self.cfg.data.mesh_size
            mesh.apply_scale(scale)
            
            return mesh
        except Exception as e:
            self.logger.error(f"Error processing mesh: {str(e)}")
            return None

    def validate_mesh(self, mesh: trimesh.Trimesh) -> bool:
        """Validate processed mesh"""
        if mesh is None:
            return False
            
        checks = [
            mesh.is_watertight,
            mesh.volume > 0,
            len(mesh.faces) > 0
        ]
        
        return all(checks)