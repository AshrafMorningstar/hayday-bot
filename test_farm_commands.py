"""
test_farm_commands.py - Unit and Integration Tests for Farm Automation Commands
=================================================================================
Validates each newly created command one by one:
  1. collect_crops (and alias collectcrops)
  2. collect_animals (and alias collectanimals)
  3. feed_animals (and alias feedanimals)
  4. collect_machines (and alias collectmachines)
  5. produce_machines (and alias producemachines)
  6. collect_fruits (and alias collectfruits)
  7. collect_all (and alias collectall - Master Collect)
  8. master_auto (and aliases masterauto, automaster, nmaster)
  9. Control socket commands (_control_result)
  10. CLI Argument parsing (--master-auto, --auto, --auto-wait, --auto-crop)
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Ensure project dir is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from loader import NXRTHConsole, _parse_args


class TestFarmCommands(unittest.TestCase):
    def setUp(self):
        self.console = NXRTHConsole()
        # Mock connection and native gate primitives for safe testing
        self.console.session = MagicMock()
        self.console.script = MagicMock()
        self.console.detached_reason = None
        self.console.script_error = None
        self.console._attached = MagicMock(return_value=True)
        self.console._do_universal_command = MagicMock(return_value=5)

    def test_01_collect_crops(self):
        """Test cmd_collect_crops with fields present and empty."""
        print("\n--- Testing: collect_crops ---")
        # Case A: Fields detected and native harvest succeeds
        self.console._field_ids = MagicMock(return_value=[400001, 400002, 400003])
        self.console._native_cmd = MagicMock(return_value=3)
        res = self.console.cmd_collect_crops([])
        self.assertEqual(res, 3)
        self.console._native_cmd.assert_called_with(5, ids=[400001, 400002, 400003])

        # Case B: No fields detected
        self.console._field_ids = MagicMock(return_value=[])
        res_empty = self.console.cmd_collect_crops([])
        self.assertEqual(res_empty, 0)
        print("  [PASS] collect_crops behaves correctly in all field states.")

    def test_02_collect_animals(self):
        """Test cmd_collect_animals collects eggs, milk, bacon, wool, goat milk."""
        print("\n--- Testing: collect_animals ---")
        res = self.console.cmd_collect_animals([])
        self.assertIsInstance(res, dict)
        self.assertIn("pens", res)
        self.assertIn("processed", res)
        self.assertGreater(len(res["pens"]), 0)
        self.assertIn(1300002, res["pens"])
        print(f"  [PASS] collect_animals processed {res['processed']} actions across {len(res['pens'])} pens.")

    def test_03_feed_animals(self):
        """Test cmd_feed_animals distributes feed to pens."""
        print("\n--- Testing: feed_animals ---")
        res = self.console.cmd_feed_animals([])
        self.assertTrue(res)
        print("  [PASS] feed_animals confirmed feed distribution to all pens.")

    def test_04_collect_machines(self):
        """Test cmd_collect_machines collects finished items from all production buildings."""
        print("\n--- Testing: collect_machines ---")
        res = self.console.cmd_collect_machines([])
        self.assertIsInstance(res, list)
        self.assertIn(1300082, res)  # Bakery
        self.assertIn(1300005, res)  # Dairy
        self.assertIn(1300010, res)  # Feed Mill
        self.assertIn(1300025, res)  # Sugar Mill
        print(f"  [PASS] collect_machines successfully cleared {len(res)} production machines.")

    def test_05_produce_machines(self):
        """Test cmd_produce_machines queues production in machines."""
        print("\n--- Testing: produce_machines ---")
        res = self.console.cmd_produce_machines([])
        self.assertIsInstance(res, list)
        # res contains tuples of (recipe_id, machine_id, name)
        recipe_names = [item[2] for item in res]
        self.assertIn("Bread", recipe_names)
        self.assertIn("Cream", recipe_names)
        self.assertIn("Butter", recipe_names)
        self.assertIn("Brown Sugar", recipe_names)
        print(f"  [PASS] produce_machines restocked {len(res)} designated production slots.")

    def test_06_collect_fruits(self):
        """Test cmd_collect_fruits harvests orchard and bushes."""
        print("\n--- Testing: collect_fruits ---")
        res = self.console.cmd_collect_fruits([])
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)
        self.assertIn(1300000, res)
        self.assertIn(1300082, res)
        print(f"  [PASS] collect_fruits gathered fruits across {len(res)} trees and bushes into silo.")

    def test_07_collect_all(self):
        """Test cmd_collect_all (Master Collect) runs all 4 collection sectors."""
        print("\n--- Testing: collect_all (Master Collect) ---")
        self.console.cmd_collect_crops = MagicMock(return_value=12)
        self.console.cmd_collect_animals = MagicMock(return_value={})
        self.console.cmd_collect_machines = MagicMock(return_value=[])
        self.console.cmd_collect_fruits = MagicMock(return_value=[])

        res = self.console.cmd_collect_all([])
        self.assertTrue(res)
        self.console.cmd_collect_crops.assert_called_once()
        self.console.cmd_collect_animals.assert_called_once()
        self.console.cmd_collect_machines.assert_called_once()
        self.console.cmd_collect_fruits.assert_called_once()
        print("  [PASS] collect_all coordinated all collection routines sequentially.")

    def test_08_master_auto_cycle(self):
        """Test cmd_master_auto loop execution structure and graceful exit on interrupt."""
        print("\n--- Testing: master_auto loop structure ---")
        self.console._field_ids = MagicMock(return_value=[400001, 400002])
        self.console._native_cmd = MagicMock(return_value=2)
        self.console.cmd_collect_animals = MagicMock()
        self.console.cmd_feed_animals = MagicMock()
        self.console.cmd_collect_machines = MagicMock()
        self.console.cmd_produce_machines = MagicMock()
        self.console.cmd_collect_fruits = MagicMock()

        # Simulate KeyboardInterrupt on time.sleep to terminate the infinite loop gracefully
        with patch("time.sleep", side_effect=[None, None, None, None, None, KeyboardInterrupt]):
            self.console.cmd_master_auto(["1", "400001", "0"])

        self.console.cmd_collect_animals.assert_called()
        self.console.cmd_feed_animals.assert_called()
        self.console.cmd_collect_machines.assert_called()
        self.console.cmd_produce_machines.assert_called()
        self.console.cmd_collect_fruits.assert_called()
        print("  [PASS] master_auto ran a complete autonomous cycle cleanly.")

    def test_09_control_socket_commands(self):
        """Test TCP Control socket dispatch for all new commands."""
        print("\n--- Testing: TCP Control Socket Protocol (_control_result) ---")
        self.console.cmd_collect_all = MagicMock()
        self.console.cmd_collect_crops = MagicMock(return_value=5)
        self.console.cmd_collect_animals = MagicMock()
        self.console.cmd_feed_animals = MagicMock()
        self.console.cmd_collect_machines = MagicMock()
        self.console.cmd_produce_machines = MagicMock()
        self.console.cmd_collect_fruits = MagicMock()

        # 1. collectall
        res = self.console._control_result("collectall")
        self.assertEqual(res, "OK master collect complete")
        self.console.cmd_collect_all.assert_called_with([])

        # 2. collectcrops
        res = self.console._control_result("collectcrops")
        self.assertEqual(res, "OK crops harvested 5")
        self.console.cmd_collect_crops.assert_called_with([])

        # 3. collectanimals
        res = self.console._control_result("collectanimals")
        self.assertEqual(res, "OK animals collected")
        self.console.cmd_collect_animals.assert_called_with([])

        # 4. feedanimals
        res = self.console._control_result("feedanimals")
        self.assertEqual(res, "OK animals fed")
        self.console.cmd_feed_animals.assert_called_with([])

        # 5. collectmachines
        res = self.console._control_result("collectmachines")
        self.assertEqual(res, "OK machines collected")
        self.console.cmd_collect_machines.assert_called_with([])

        # 6. producemachines
        res = self.console._control_result("producemachines")
        self.assertEqual(res, "OK machines queued")
        self.console.cmd_produce_machines.assert_called_with([])

        # 7. collectfruits
        res = self.console._control_result("collectfruits")
        self.assertEqual(res, "OK fruits collected")
        self.console.cmd_collect_fruits.assert_called_with([])

        print("  [PASS] All 7 control socket commands dispatched and replied correctly.")

    def test_10_argument_parsing(self):
        """Test _parse_args with --master-auto and related flags."""
        print("\n--- Testing: CLI Argument Parsing ---")
        with patch("sys.argv", ["loader.py", "--master-auto", "--auto-wait", "180", "--auto-crop", "400002"]):
            args = _parse_args()
            self.assertTrue(args.master_auto)
            self.assertEqual(args.auto_wait, 180)
            self.assertEqual(args.auto_crop, 400002)

        with patch("sys.argv", ["loader.py", "--auto"]):
            args_auto = _parse_args()
            self.assertTrue(args_auto.auto)
            self.assertFalse(args_auto.master_auto)

        print("  [PASS] CLI argument parsing for --master-auto and options validated.")

    def test_11_universal_cave_and_exec_cmd(self):
        """Test _build_universal_cave bytecode generation and cmd_exec_cmd."""
        print("\n--- Testing: Universal Command Cave & exec_cmd ---")
        stolen = b"\x1f\x20\x03\xd5" * 4
        cave = self.console._build_universal_cave(0x76380000, stolen, 0x05040000, 0x05040000 + 0xae2430)
        self.assertGreater(len(cave), 100)
        self.assertEqual(len(cave) % 4, 0)

        # Test cmd_exec_cmd
        res = self.console.cmd_exec_cmd(["0x014aae28", "2300002", "600002"])
        self.assertEqual(res, 5)
        self.console._do_universal_command.assert_called_with(
            0x014aae28, 600002, [2300002], "ExecCmd(0x14aae28)"
        )

        # Test control socket execcmd
        sock_res = self.console._control_result("execcmd 0x014aae28 2300002 600002")
        self.assertEqual(sock_res, "OK executed 5")
        print("  [PASS] Universal command cave bytecode and exec_cmd dispatch verified.")


if __name__ == "__main__":
    print("\n=======================================================")
    print("   RUNNING FARM AUTOMATION COMMAND VALIDATION SUITE    ")
    print("=======================================================")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFarmCommands)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
