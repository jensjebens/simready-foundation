# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Requirement:
    """
    Args:
        code: A unique identifier of the requirement
        display_name: A human-readable name of the requirement
        message: A basic description of the requirement
        path: Relative path in documentation
        compatibility: Compatibility of the requirement
        tags: Tags of the requirement
    """

    code: str
    display_name: str
    message: str
    path: Optional[str] = None
    compatibility: Optional[str] = None
    tags: Tuple[str, ...] = ()


from .core.atomic_asset import validation
import logging as _logging
_logger = _logging.getLogger(__name__)

def _safe_import(module_path):
    """Import a validation module, logging failures without stopping the chain."""
    try:
        __import__(module_path, fromlist=["validation"])
    except Exception as e:
        _logger.warning("Failed to load %s: %s", module_path, e)

_safe_import("capabilities.core.atomic_asset.validation")
_safe_import("capabilities.core.naming_paths.validation")
_safe_import("capabilities.core.sim_ready.validation")
_safe_import("capabilities.core.units.validation")
_safe_import("capabilities.hierarchy.validation")
_safe_import("capabilities.isaac_sim.composition.validation")
_safe_import("capabilities.isaac_sim.robot_core.validation")
_safe_import("capabilities.isaac_sim.robot_materials.validation")
_safe_import("capabilities.nonvisual_sensors.nonvisual_materials.validation")
_safe_import("capabilities.physics_bodies.base_articulation.validation")
_safe_import("capabilities.physics_bodies.physics_colliders.validation")
_safe_import("capabilities.physics_bodies.physics_driven_joints.validation")
_safe_import("capabilities.physics_bodies.physics_graspable.validation")
_safe_import("capabilities.physics_bodies.physics_joints.validation")
_safe_import("capabilities.physics_bodies.physics_materials.validation")
_safe_import("capabilities.physics_bodies.physics_rigid_bodies.validation")
_safe_import("capabilities.semantic_labels.validation")
_safe_import("capabilities.visualization.geometry.validation")
_safe_import("capabilities.visualization.materials.validation")
