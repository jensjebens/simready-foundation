# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""
OAV entrypoint plugin for SimReady Foundation validation rules.

Registers all SRF checkers and loads the capability DAG into OAV registries.
Based on Miguel's setUp() pattern for patching missing symbols and triggering
decorator-based rule registration via capabilities import.
"""
from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)


class SimReadyPlugin:
    """
    Plugin that registers SimReady Foundation validation rules and loads
    the capability DAG.

    Implements the PluginProtocol for OAV's entrypoint plugin system.
    """

    def __init__(self):
        self._caps = []
        self._feats = []
        self._profs = []

    def _patch_missing_symbols(self) -> None:
        """Patch missing symbols on omni.asset_validator if needed."""
        # Import the module directly (don't trigger PluginManager yet)
        import omni.asset_validator as av

        # Patch is_omni_path (Kit-specific utility not in standalone OAV)
        if not hasattr(av, "is_omni_path"):
            from pxr import Sdf

            _OMNI_PRIM_PATHS = {
                Sdf.Path("/OmniverseKit_Persp"),
                Sdf.Path("/OmniverseKit_Front"),
                Sdf.Path("/OmniverseKit_Top"),
                Sdf.Path("/OmniverseKit_Right"),
                Sdf.Path("/OmniKit_Viewport_LightRig"),
            }
            _OMNI_PRIM_NAMES = {"OmniverseKitViewportCameraMesh"}

            def is_omni_path(path: Sdf.Path) -> bool:
                return path in _OMNI_PRIM_PATHS or path.name in _OMNI_PRIM_NAMES

            av.is_omni_path = is_omni_path

        # Patch registerRule (camelCase legacy alias)
        if not hasattr(av, "registerRule"):
            if hasattr(av, "register_rule"):
                av.registerRule = av.register_rule
            else:
                # Try importing from categories
                try:
                    from omni.asset_validator._categories import register_rule
                    av.registerRule = register_rule
                except ImportError:
                    pass

    def _load_srf_checkers(self) -> None:
        """Import SRF capabilities package to trigger all validation decorators.

        SRF's capabilities/__init__.py chain-imports all validation.py modules,
        which triggers @register_rule / @register_requirements decorators.
        """
        import importlib
        import os

        # Find the SRF capabilities directory
        srf_caps_dir = os.environ.get("SIMREADY_SPECS_PATH")
        if not srf_caps_dir:
            # Try relative to this package
            from pathlib import Path

            candidates = [
                Path(__file__).parent.parent.parent
                / "simready-foundation"
                / "nv_core"
                / "sr_specs"
                / "docs"
                / "capabilities",
            ]
            for c in candidates:
                if c.exists():
                    srf_caps_dir = str(c)
                    break

        if not srf_caps_dir:
            logger.info("SRF specs not found; using generated capabilities only")
            try:
                from . import capabilities  # noqa: F401
            except Exception as e:
                logger.warning("Failed to import capabilities: %s", e)
            return

        # Add the parent directory so 'capabilities' resolves as a package
        parent_dir = os.path.dirname(srf_caps_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        try:
            # Force reimport if already loaded (e.g. from generated package)
            if "capabilities" in sys.modules:
                importlib.reload(sys.modules["capabilities"])
            else:
                import capabilities  # noqa: F811, F401

            logger.info("SRF capabilities chain-import complete (all checkers registered)")
        except Exception as e:
            logger.warning("Failed to chain-import SRF capabilities: %s", e)
            # Fall back to generated capabilities
            try:
                from . import capabilities  # noqa: F401
            except Exception:
                pass

    def _load_capability_graph(self) -> None:
        """Load the DAG and populate OAV registries."""
        try:
            from omni.usd_profiles.graph import CapabilityGraph

            from . import get_capabilities_json_path

            graph = CapabilityGraph()
            graph.load_from_json(get_capabilities_json_path())
            logger.info(
                "Loaded capability graph: %d nodes, %d profiles",
                len(graph),
                len(graph.get_all_profiles()),
            )

            from omni.asset_validator._graph_loader import load_capability_graph

            self._caps, self._feats, self._profs = load_capability_graph(graph)

        except ImportError as e:
            logger.warning("Graph loader not available: %s", e)
        except Exception as e:
            logger.error("Failed to load capability graph: %s", e)

    def on_startup(self) -> None:
        """Register SRF checkers and load capability DAG."""
        logger.info("Starting SimReady Foundation plugin")

        # Step 1: Patch missing symbols (Miguel's approach)
        self._patch_missing_symbols()

        # Step 2: Import capabilities to trigger checker registration
        self._load_srf_checkers()

        # Step 3: Load DAG into OAV registries
        self._load_capability_graph()

        logger.info("SimReady Foundation plugin started successfully")

    def on_shutdown(self) -> None:
        """Unregister everything."""
        try:
            from omni.asset_validator._graph_loader import unload_capability_graph

            unload_capability_graph(self._caps, self._feats, self._profs)
        except ImportError:
            pass

        self._caps.clear()
        self._feats.clear()
        self._profs.clear()
        logger.info("SimReady Foundation plugin shutdown complete")
