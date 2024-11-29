import json
import trimesh
import logging

import numpy as np

from omegaconf import DictConfig
from typing import Dict, List, Optional

from src.helpers.logger import logme


class SceneLoader:
    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        self.logger = logging.getLogger(__name__)
        
    def load_scene_json(self, scene_path: str) -> Dict:
        """Load scene JSON file from 3D-FRONT dataset"""
        try:
            with open(scene_path, 'r') as f:
                scene_data = json.load(f)
            return scene_data
        except Exception as e:
            self.logger.error(f"Error loading scene {scene_path}: {str(e)}")
            return None

    def validate_scene_size(self, scene_data: Dict) -> bool:
        """Check if scene fits within size constraints"""
        # Extract scene dimensions
        bbox = self._compute_scene_bbox(scene_data)
        max_dims = np.array([512, 512, 128]) * self.cfg.data.mesh_size
        
        return all(bbox[1] - bbox[0] <= max_dims)

    def _compute_scene_bbox(self, scene_data: Dict) -> np.ndarray:
        """Compute scene bounding box from furniture placements"""
        furniture_positions = []
        # for room in scene_data['rooms']:
        for furniture in scene_data['furniture']:
                pos = np.array(furniture['pos'])
                furniture_positions.append(pos)
        
        positions = np.stack(furniture_positions)
        min_pos = np.min(positions, axis=0)
        max_pos = np.max(positions, axis=0)
        
        return np.stack([min_pos, max_pos])