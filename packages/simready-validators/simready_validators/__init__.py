# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""
SimReady validators package.

Provides:
- A capabilities.json DAG definition for the SimReady capability graph
- An OAV entrypoint plugin that bridges the DAG into OAV's registries
"""

import os

__all__ = ["get_capabilities_json_path"]

_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_capabilities_json_path() -> str:
    """Return the path to the bundled capabilities.json."""
    return os.path.join(_PACKAGE_DIR, "resources", "capabilities.json")
