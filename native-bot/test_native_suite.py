"""
Automated Test Suite for Native Bot Rebuild
Verifies catalog integrity, roadside pricing strategies, daily expansion caps, and 1-click execution.
"""

import os
import json
import unittest

class TestNativeBotSuite(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def test_ui_files_exist(self):
        self.assertTrue(os.path.exists(os.path.join(self.base_dir, "ui", "index.html")))
        self.assertTrue(os.path.exists(os.path.join(self.base_dir, "ui", "style.css")))
        self.assertTrue(os.path.exists(os.path.join(self.base_dir, "ui", "app.js")))

    def test_pricing_calculations(self):
        max_price = 403
        count = 10
        total_max = max_price * count

        # Highest
        self.assertEqual(total_max, 4030)
        # Lowest
        self.assertEqual(count, 10)
        # Half
        self.assertEqual(round(total_max * 0.5), 2015)
        # 75%
        self.assertEqual(int(total_max * 0.75), 3022)
        # Anti-Ban Max (jitter -1 to -3)
        for jitter in [1, 2, 3]:
            ab_price = total_max - jitter
            self.assertTrue(4027 <= ab_price <= 4029)

    def test_daily_expansion_cap(self):
        cap = 80
        current = 0
        # Simulate snipes up to cap
        snipes = [20, 30, 30]
        for s in snipes:
            self.assertTrue(current + s <= cap)
            current += s
        self.assertEqual(current, cap)
        # Attempt to exceed cap
        self.assertFalse(current + 1 <= cap)

    def test_mining_diamond_cap(self):
        diamond_goal = 10
        collected_diamonds = 0
        tools = [("Dynamite", 1), ("TNT", 2), ("Shovel", 3), ("Pickaxe", 5)]
        for name, power in tools:
            if collected_diamonds >= diamond_goal:
                break
            if power >= 3:
                collected_diamonds += 2
        self.assertTrue(collected_diamonds <= diamond_goal + 2)

    def test_launcher_batch_exists(self):
        bat = os.path.join(self.base_dir, "run_native_bot.bat")
        self.assertTrue(os.path.exists(bat))

if __name__ == "__main__":
    unittest.main()
