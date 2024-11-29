# src/processing/blender_processor.py
import os
import bpy
import bmesh
import logging

import numpy as np

from omegaconf import DictConfig
from typing import Optional, Tuple

from src.helpers.logger import logme


class BlenderProcessor:
    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        self.logger = logging.getLogger(__name__)
        
    def process_scene(self, input_path: str, output_path: str) -> bool:
        """Process scene mesh using Blender"""
        try:
            # Clear existing scene
            bpy.ops.wm.read_factory_settings()
            
            # Import mesh
            if input_path.endswith('.obj'):
                bpy.ops.import_scene.obj(filepath=input_path)
            else:
                self.logger.error(f"Unsupported file format: {input_path}")
                return False
                
            # Get the imported object
            obj = bpy.context.selected_objects[0]
            
            # Apply modifiers for mesh cleanup
            self._apply_cleanup_modifiers(obj)
            
            # Perform voxel remeshing
            self._apply_voxel_remesh(obj, self.cfg.data.mesh_size)
            
            # Export processed mesh
            bpy.ops.export_scene.obj(
                filepath=output_path,
                use_selection=True,
                use_materials=False
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in Blender processing: {str(e)}")
            return False
            
    def _apply_cleanup_modifiers(self, obj: bpy.types.Object) -> None:
        """Apply cleanup modifiers to mesh"""
        # Remove doubles
        mod = obj.modifiers.new(name="Remove Doubles", type='WELD')
        mod.merge_threshold = 0.0001
        bpy.ops.object.modifier_apply(modifier=mod.name)
        
        # Fill holes
        mod = obj.modifiers.new(name="Fill Holes", type='SOLIDIFY')
        mod.thickness = 0.0001
        bpy.ops.object.modifier_apply(modifier=mod.name)
        
    def _apply_voxel_remesh(self, obj: bpy.types.Object, voxel_size: float) -> None:
        """Apply voxel remeshing"""
        mod = obj.modifiers.new(name="Voxel Remesh", type='REMESH')
        mod.mode = 'VOXEL'
        mod.voxel_size = voxel_size
        bpy.ops.object.modifier_apply(modifier=mod.name)