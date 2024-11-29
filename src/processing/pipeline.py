import os
import json
import logging

import numpy as np

from tqdm import tqdm
from pathlib import Path
from omegaconf import DictConfig
from dataclasses import dataclass
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

try:
    from src.helpers.logger import logme
    from src.data.scene_loader import SceneLoader
    from src.processing.mesh_processor import MeshProcessor
    from src.processing.blender_processor import BlenderProcessor
    from src.processing.sdf_generator import SDFGenerator
    from src.visualization.visualizer import SceneVisualizer
except ImportError as e:
    logging.error(f"Failed to import required modules: {str(e)}")
    raise


class ProcessingPipeline:
    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.scene_loader = SceneLoader(cfg)
        self.mesh_processor = MeshProcessor(cfg)
        self.blender_processor = BlenderProcessor(cfg)
        self.sdf_generator = SDFGenerator(cfg)
        self.visualizer = SceneVisualizer(cfg)
        
        logme("Initialized components for data processing.")
        
    def process_scene(self, scene_path: str) -> bool:
        """Process single scene through pipeline"""
        try:
            # Load scene
            scene_data = self.scene_loader.load_scene_json(scene_path)
            if scene_data is None:
                return False
                
            # Validate scene size
            if not self.scene_loader.validate_scene_size(scene_data):
                self.logger.info(f"Scene {scene_path} exceeds size limits")
                return False
                
            # Process paths
            scene_id = os.path.splitext(os.path.basename(scene_path))[0]
            temp_dir = os.path.join(self.cfg.data.output_dir, "temp", scene_id)
            os.makedirs(temp_dir, exist_ok=True)
            
            # Initial mesh processing
            input_mesh = os.path.join(temp_dir, "input.obj")
            processed_mesh = os.path.join(temp_dir, "processed.obj")
            
            if not self.mesh_processor.process_mesh(input_mesh):
                return False
                
            # Blender processing
            if not self.blender_processor.process_scene(processed_mesh, 
                                                      os.path.join(temp_dir, "remeshed.obj")):
                return False
                
            # Generate SDF/TSDF
            tsdf = self.sdf_generator.generate_sdf(
                os.path.join(temp_dir, "remeshed.obj"),
                os.path.join(self.cfg.data.output_dir, f"{scene_id}_tsdf.npy")
            )
            
            if tsdf is None:
                return False
                
            # Visualize results
            self.visualizer.visualize_mesh(
                processed_mesh,
                os.path.join(self.cfg.data.output_dir, f"{scene_id}_vis.png")
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing scene {scene_path}: {str(e)}")
            return False
            
    def process_dataset(self) -> None:
        """Process entire dataset with parallel execution"""
        scene_paths = self._get_scene_paths()
        
        with ThreadPoolExecutor(max_workers=self.cfg.processing.num_workers) as executor:
            list(tqdm(
                executor.map(self.process_scene, scene_paths),
                total=len(scene_paths),
                desc="Processing scenes"
            ))
            
    def _get_scene_paths(self) -> List[str]:
        """Get list of scene paths to process"""
        scene_dir = os.path.join(self.cfg.data.root_dir, "3d_front")
        logme(f"The established scene dir: {scene_dir}")
        scene_paths = []
        
        for filename in os.listdir(scene_dir):
            if filename.endswith('.json'):
                scene_paths.append(os.path.join(scene_dir, filename))
                
        return scene_paths