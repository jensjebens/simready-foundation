# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Tests for the SimReady validators adapter and plugin."""

import os
import sys
import unittest

# Ensure the packages are importable
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _BASE)
sys.path.insert(0, os.path.join(os.path.dirname(_BASE), "open-usd-profiles"))


class TestCapabilitiesJsonBundled(unittest.TestCase):
    """Verify the bundled capabilities.json exists and is valid."""

    def test_json_exists(self):
        from simready_validators import get_capabilities_json_path
        path = get_capabilities_json_path()
        self.assertTrue(os.path.exists(path), f"Missing: {path}")

    def test_json_loads(self):
        import json
        from simready_validators import get_capabilities_json_path
        with open(get_capabilities_json_path()) as f:
            data = json.load(f)
        self.assertEqual(data["schema"], "usd-profiles/capability-dag/v2")
        self.assertGreater(len(data["capabilities"]), 0)


class TestAdapter(unittest.TestCase):
    """Tests for the OAV adapter that converts DAG → OAV objects."""

    def setUp(self):
        from omni.usd_profiles.graph import CapabilityGraph
        from simready_validators import get_capabilities_json_path

        self.graph = CapabilityGraph()
        self.graph.load_from_json(get_capabilities_json_path())

    def test_build_oav_objects_returns_three_lists(self):
        from simready_validators.adapter import build_oav_objects
        caps, feats, profs = build_oav_objects(self.graph)
        self.assertIsInstance(caps, list)
        self.assertIsInstance(feats, list)
        self.assertIsInstance(profs, list)

    def test_capabilities_have_required_fields(self):
        from simready_validators.adapter import build_oav_objects
        caps, _, _ = build_oav_objects(self.graph)
        self.assertGreater(len(caps), 0)
        for cap in caps:
            self.assertTrue(hasattr(cap, "id"))
            self.assertTrue(hasattr(cap, "version"))
            self.assertTrue(hasattr(cap, "path"))
            self.assertTrue(hasattr(cap, "requirements"))

    def test_features_have_required_fields(self):
        from simready_validators.adapter import build_oav_objects
        _, feats, _ = build_oav_objects(self.graph)
        # Features may be empty if the SRF codegen didn't include them
        for feat in feats:
            self.assertTrue(hasattr(feat, "id"))
            self.assertTrue(hasattr(feat, "version"))
            self.assertTrue(hasattr(feat, "requirements"))

    def test_profiles_have_required_fields(self):
        from simready_validators.adapter import build_oav_objects
        _, _, profs = build_oav_objects(self.graph)
        self.assertGreater(len(profs), 0)
        for prof in profs:
            self.assertTrue(hasattr(prof, "id"))
            self.assertTrue(hasattr(prof, "version"))
            self.assertTrue(hasattr(prof, "capabilities"))

    def test_profiles_exist(self):
        from simready_validators.adapter import build_oav_objects
        _, _, profs = build_oav_objects(self.graph)
        self.assertGreater(len(profs), 0, "Expected at least one profile")
        # Note: profile→capability linkage requires feature ID resolution
        # between TOML profile refs (FET001_BASE_NEUTRAL) and markdown
        # feature IDs (fet_001_minimal). This is tracked as a known gap.

    def test_requirements_have_code(self):
        from simready_validators.adapter import build_oav_objects, OavRequirement
        caps, _, _ = build_oav_objects(self.graph)
        for cap in caps:
            for req in cap.requirements:
                self.assertIsInstance(req, OavRequirement)
                self.assertTrue(req.code, f"Requirement missing code in {cap.id}")

    def test_no_duplicate_requirements(self):
        from simready_validators.adapter import build_oav_objects
        caps, _, _ = build_oav_objects(self.graph)
        all_codes = []
        for cap in caps:
            for req in cap.requirements:
                all_codes.append(req.code)
        # Codes can repeat across capabilities but within a capability should be unique
        for cap in caps:
            codes = [r.code for r in cap.requirements]
            self.assertEqual(len(codes), len(set(codes)),
                             f"Duplicate requirements in {cap.id}")


class TestPlugin(unittest.TestCase):
    """Tests for the SimReadyPlugin lifecycle."""

    def test_plugin_instantiates(self):
        from simready_validators.plugin import SimReadyPlugin
        plugin = SimReadyPlugin()
        self.assertIsNotNone(plugin)

    def test_plugin_startup_loads_graph(self):
        """Plugin on_startup should not crash even without OAV."""
        from simready_validators.plugin import SimReadyPlugin
        plugin = SimReadyPlugin()
        # on_startup will log a warning if OAV isn't available, but shouldn't crash
        plugin.on_startup()
        plugin.on_shutdown()


if __name__ == "__main__":
    unittest.main(verbosity=2)
