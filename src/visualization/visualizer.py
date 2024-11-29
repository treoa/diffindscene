import logging
import trimesh

import numpy as np
import matplotlib.pyplot as plt

from typing import Optional
from omegaconf import DictConfig

from src.helpers.logger import logger


class SceneVisualizer:
    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        self.logger = logging.getLogger(__name__)
        
    def visualize_mesh(self, mesh: trimesh.Trimesh, 
                      output_path: Optional[str] = None) -> None:
        """Visualize mesh with quality metrics"""
        try:
            # Create figure with multiple views
            fig = plt.figure(figsize=(15, 5))
            
            # Original mesh
            ax1 = fig.add_subplot(131, projection='3d')
            self._plot_mesh(ax1, mesh, 'Original Mesh')
            
            # Mesh quality heatmap
            ax2 = fig.add_subplot(132)
            quality = self._compute_mesh_quality(mesh)
            self._plot_quality_heatmap(ax2, quality, 'Mesh Quality')
            
            # Cross sections
            ax3 = fig.add_subplot(133)
            self._plot_cross_sections(ax3, mesh, 'Cross Sections')
            
            if output_path:
                plt.savefig(output_path)
            plt.close()
            
        except Exception as e:
            self.logger.error(f"Error visualizing mesh: {str(e)}")

    def _compute_mesh_quality(self, mesh: trimesh.Trimesh) -> np.ndarray:
        """Compute mesh quality metrics"""
        # Compute aspect ratios of faces
        aspects = []
        for face in mesh.faces:
            vertices = mesh.vertices[face]
            edges = np.roll(vertices, -1, axis=0) - vertices
            lengths = np.linalg.norm(edges, axis=1)
            aspect = np.max(lengths) / np.min(lengths)
            aspects.append(aspect)
        return np.array(aspects)