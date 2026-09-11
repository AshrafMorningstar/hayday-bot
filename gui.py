"""
gui.py - Modern Graphical User Interface for Hay Day Bot & Memory Injector
==========================================================================
Provides an intuitive, dark-mode desktop interface:
  1. Action Selection: Choose exactly what you want to automate (Crops, Animals, Machines, Fruits, Selling)
  2. Emergency Stop & Halt: Instantly pause or terminate all automated actions on demand
  3. One-Click Manual Actions: Collect All, Harvest Crops, Feed Livestock, Clear Machines, etc.
  4. Custom Command Builder: Execute any captured vtable + targetId + param2 directly
  5. Live Log Stream & Interactive Terminal
  6. Screenshot & Feature Request Assistant
"""

import sys
import os
import socket
import threading
import time
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from game_ids import search_id, ALL_CATEGORIES

HOST = "127.0.0.1"
PORT = 31350

# Pre-analyzed captured commands for quick selection
CAPTURED_COMMANDS = {
    "Feed Animal (0x014aae28)": {
        "vtable": "0x014aae28",
        "desc": "Feeds livestock (Chicken, Cow, Pig, Sheep, Goat)",
        "target_label": "Animal ID (e.g. 2300002)",
        "param_label": "Feed ID (e.g. 600002 Chicken Feed)",
        "default_target": "2300002",
        "default_param": "600002"
    },
    "Collect Building / Machine (0x014a63f8)": {
        "vtable": "0x014a63f8",
        "desc": "Collects finished products from Bakery, Dairy, Sugar Mill, etc.",
        "target_label": "Building ID (e.g. 1300082 Bakery)",
        "param_label": "Param 2 (Default: 0)",
        "default_target": "1300082",
        "default_param": "0"
    },
    "Collect Animal Products (0x014a7d88)": {
        "vtable": "0x014a7d88",
        "desc": "Collects eggs, milk, bacon, wool from animal pens",
        "target_label": "Pen ID (e.g. 1300002)",
        "param_label": "Param 2 (Default: 0)",
        "default_target": "1300002",
        "default_param": "0"
    },
    "Start Machine Production (0x014a9cc8)": {
        "vtable": "0x014a9cc8",
        "desc": "Starts producing item in machine queue (Bread, Cream, etc.)",
        "target_label": "Recipe ID (e.g. 1100015 Bread)",
        "param_label": "Machine ID (e.g. 1300082 Bakery)",
        "default_target": "1100015",
        "default_param": "1300082"
    },
    "Select Building (0x014aef68)": {
        "vtable": "0x014aef68",
        "desc": "Selects / highlights a building or structure",
        "target_label": "Building ID (e.g. 1300002)",
        "param_label": "Param 2 (Default: 0)",
        "default_target": "1300002",
        "default_param": "0"
    },
    "Custom / Manual Vtable": {
        "vtable": "",
        "desc": "Enter any arbitrary captured vtable offset and parameters",
        "target_label": "Target ID (+24)",
        "param_label": "Param 2 (+28)",
        "default_target": "0",
        "default_param": "0"
    }
}


class HayDayBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌾 Hay Day Bot - Automation Controller & Memory Gate")
        self.root.geometry("1040x780")
        self.root.minsize(920, 680)
        self.root.configure(bg="#181825")

        self.sock = None
        self.connected = False
        self.backend_proc = None
        self.running_auto = False

        self._apply_styles()
        self._build_header()
        self._build_tabs()
        self._build_status_bar()

        # Start background polling thread for TCP socket connection
        self.poll_thread = threading.Thread(target=self._auto_connect_loop, daemon=True)
        self.poll_thread.start()

    def _apply_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Palette: Catppuccin Mocha / Dark Cyberpunk
        self.bg_dark = "#181825"
        self.bg_card = "#1e1e2e"
        self.bg_card_highlight = "#313244"
        self.fg_main = "#cdd6f4"
        self.fg_sub = "#a6adc8"
        self.accent_green = "#a6e3a1"
        self.accent_blue = "#89b4fa"
        self.accent_yellow = "#f9e2af"
        self.accent_red = "#f38ba8"
        self.accent_purple = "#cba6f7"

        self.style.configure("TNotebook", background=self.bg_dark, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.bg_card, foreground=self.fg_main,
                               padding=[18, 8], font=("Segoe UI", 10, "bold"), borderwidth=0)
        self.style.map("TNotebook.Tab",
                       background=[("selected", self.accent_purple)],
                       foreground=[("selected", "#11111b")])

        self.style.configure("Card.TFrame", background=self.bg_card, relief="flat")
        self.style.configure("TLabel", background=self.bg_card, foreground=self.fg_main, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", background=self.bg_dark, foreground="#ffffff", font=("Segoe UI", 16, "bold"))
        self.style.configure("SubHeader.TLabel", background=self.bg_dark, foreground=self.fg_sub, font=("Segoe UI", 9))

    def _build_header(self):
        header_frame = tk.Frame(self.root, bg=self.bg_dark, pady=12, padx=20)
        header_frame.pack(fill=tk.X)

        title_box = tk.Frame(header_frame, bg=self.bg_dark)
        title_box.pack(side=tk.LEFT)

        title_lbl = tk.Label(title_box, text="🌾 HAY DAY MEMORY GATE & BOT", font=("Segoe UI", 16, "bold"),
                             fg="#ffffff", bg=self.bg_dark)
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(title_box, text="ARM64 Universal Gate · Configurable Automation · Interactive Control",
                           font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_dark)
        sub_lbl.pack(anchor="w")

        # Right control panel in header
        right_box = tk.Frame(header_frame, bg=self.bg_dark)
        right_box.pack(side=tk.RIGHT)

        self.status_pill = tk.Label(right_box, text="● DISCONNECTED", font=("Segoe UI", 9, "bold"),
                                    fg=self.accent_red, bg=self.bg_card, padx=12, pady=5)
        self.status_pill.pack(side=tk.LEFT, padx=8)

        self.btn_backend = tk.Button(right_box, text="🚀 Connect / Start Backend", font=("Segoe UI", 9, "bold"),
                                     bg=self.accent_blue, fg="#11111b", activebackground=self.accent_purple,
                                     relief="flat", padx=12, pady=5, cursor="hand2", command=self._launch_backend)
        self.btn_backend.pack(side=tk.LEFT, padx=4)

        # Global Emergency Stop in Header
        self.btn_header_stop = tk.Button(right_box, text="🛑 STOP ALL", font=("Segoe UI", 9, "bold"),
                                         bg=self.accent_red, fg="#ffffff", activebackground="#cf6679",
                                         relief="flat", padx=12, pady=5, cursor="hand2", command=self._stop_all)
        self.btn_header_stop.pack(side=tk.LEFT, padx=4)

    def _build_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        self.tab_dashboard = tk.Frame(self.notebook, bg=self.bg_dark)
        self.tab_shop = tk.Frame(self.notebook, bg=self.bg_dark)
        self.tab_teleport = tk.Frame(self.notebook, bg=self.bg_dark)
        self.tab_builder = tk.Frame(self.notebook, bg=self.bg_dark)
        self.tab_id_finder = tk.Frame(self.notebook, bg=self.bg_dark)
        self.tab_logs = tk.Frame(self.notebook, bg=self.bg_dark)
        self.tab_screenshot = tk.Frame(self.notebook, bg=self.bg_dark)
        self.tab_help = tk.Frame(self.notebook, bg=self.bg_dark)

        self.notebook.add(self.tab_dashboard, text="  🚜 Farm Dashboard  ")
        self.notebook.add(self.tab_shop, text="  🏪 Roadside Shop & Auto-Sell  ")
        self.notebook.add(self.tab_teleport, text="  🚀 Screen Teleport  ")
        self.notebook.add(self.tab_builder, text="  ⚡ Custom Command Builder  ")
        self.notebook.add(self.tab_id_finder, text="  🔍 ID Code Finder  ")
        self.notebook.add(self.tab_logs, text="  📋 Live Logs & Terminal  ")
        self.notebook.add(self.tab_screenshot, text="  📸 Screenshot & Features  ")
        self.notebook.add(self.tab_help, text="  📖 Command Guide  ")

        self._init_dashboard_tab()
        self._init_shop_tab()
        self._init_teleport_tab()
        self._init_builder_tab()
        self._init_id_finder_tab()
        self._init_logs_tab()
        self._init_screenshot_tab()
        self._init_help_tab()

    def _init_dashboard_tab(self):
        # 1. Option Selector Card (WHAT ARE YOU GOING TO DO?)
        option_card = tk.Frame(self.tab_dashboard, bg=self.bg_card, padx=16, pady=12, relief="flat",
                               highlightbackground=self.accent_blue, highlightthickness=1)
        option_card.pack(fill=tk.X, padx=15, pady=(10, 6))

        tk.Label(option_card, text="⚙️ STEP 1: CHOOSE WHAT YOU WANT TO DO", font=("Segoe UI", 11, "bold"),
                 fg=self.accent_blue, bg=self.bg_card).pack(anchor="w")

        tk.Label(option_card, text="Select the exact sectors you wish to automate. Unchecked sectors will not be touched.",
                 font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card).pack(anchor="w", pady=(1, 8))

        # Checkbox Grid
        chk_frame = tk.Frame(option_card, bg=self.bg_card)
        chk_frame.pack(fill=tk.X, pady=2)

        self.opt_crops = tk.BooleanVar(value=True)
        self.opt_animals = tk.BooleanVar(value=True)
        self.opt_feed = tk.BooleanVar(value=True)
        self.opt_machines = tk.BooleanVar(value=True)
        self.opt_produce = tk.BooleanVar(value=True)
        self.opt_fruits = tk.BooleanVar(value=True)
        self.opt_sell = tk.BooleanVar(value=False)

        cb1 = tk.Checkbutton(chk_frame, text="🌾 Harvest & Replant Crops", variable=self.opt_crops,
                             bg=self.bg_card, fg=self.fg_main, selectcolor="#11111b", activebackground=self.bg_card, font=("Segoe UI", 9, "bold"))
        cb1.grid(row=0, column=0, sticky="w", padx=8, pady=3)

        cb2 = tk.Checkbutton(chk_frame, text="🐔 Collect Animal Goods", variable=self.opt_animals,
                             bg=self.bg_card, fg=self.fg_main, selectcolor="#11111b", activebackground=self.bg_card, font=("Segoe UI", 9, "bold"))
        cb2.grid(row=0, column=1, sticky="w", padx=8, pady=3)

        cb3 = tk.Checkbutton(chk_frame, text="🥣 Feed Livestock Pens", variable=self.opt_feed,
                             bg=self.bg_card, fg=self.fg_main, selectcolor="#11111b", activebackground=self.bg_card, font=("Segoe UI", 9, "bold"))
        cb3.grid(row=0, column=2, sticky="w", padx=8, pady=3)

        cb4 = tk.Checkbutton(chk_frame, text="🏭 Collect Finished Machine Items", variable=self.opt_machines,
                             bg=self.bg_card, fg=self.fg_main, selectcolor="#11111b", activebackground=self.bg_card, font=("Segoe UI", 9, "bold"))
        cb4.grid(row=1, column=0, sticky="w", padx=8, pady=3)

        cb5 = tk.Checkbutton(chk_frame, text="🍞 Queue Production Slots", variable=self.opt_produce,
                             bg=self.bg_card, fg=self.fg_main, selectcolor="#11111b", activebackground=self.bg_card, font=("Segoe UI", 9, "bold"))
        cb5.grid(row=1, column=1, sticky="w", padx=8, pady=3)

        cb6 = tk.Checkbutton(chk_frame, text="🍎 Harvest Trees & Berry Bushes", variable=self.opt_fruits,
                             bg=self.bg_card, fg=self.fg_main, selectcolor="#11111b", activebackground=self.bg_card, font=("Segoe UI", 9, "bold"))
        cb6.grid(row=1, column=2, sticky="w", padx=8, pady=3)

        cb7 = tk.Checkbutton(chk_frame, text="💰 Auto-Sell Surplus in Shop", variable=self.opt_sell,
                             bg=self.bg_card, fg=self.fg_main, selectcolor="#11111b", activebackground=self.bg_card, font=("Segoe UI", 9))
        cb7.grid(row=2, column=0, sticky="w", padx=8, pady=3)

        # Settings row (Delay & Crop ID)
        set_row = tk.Frame(option_card, bg=self.bg_card)
        set_row.pack(fill=tk.X, pady=(6, 2))

        tk.Label(set_row, text="Cycle Delay (sec):", font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card).pack(side=tk.LEFT)
        self.entry_delay = tk.Entry(set_row, width=6, font=("Consolas", 9), bg=self.bg_dark, fg="#ffffff", insertbackground="#ffffff", relief="flat")
        self.entry_delay.pack(side=tk.LEFT, padx=(4, 16), ipady=2)
        self.entry_delay.insert(0, "130")

        tk.Label(set_row, text="Crop ID:", font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card).pack(side=tk.LEFT)
        self.crop_var = tk.StringVar(value="400001 (Wheat)")
        crop_combo = ttk.Combobox(set_row, textvariable=self.crop_var, values=["400001 (Wheat)", "400002 (Corn)", "400003 (Soybean)", "400004 (Sugarcane)", "400005 (Carrot)"], width=18, state="readonly")
        crop_combo.pack(side=tk.LEFT, padx=4)

        # 2. Master Execution & Emergency Stop Card
        exec_card = tk.Frame(self.tab_dashboard, bg=self.bg_card, padx=16, pady=12, relief="flat",
                             highlightbackground=self.accent_purple, highlightthickness=1)
        exec_card.pack(fill=tk.X, padx=15, pady=6)

        tk.Label(exec_card, text="🚀 STEP 2: RUN OR STOP COMMANDS", font=("Segoe UI", 11, "bold"),
                 fg=self.accent_purple, bg=self.bg_card).pack(anchor="w")

        btn_row = tk.Frame(exec_card, bg=self.bg_card)
        btn_row.pack(fill=tk.X, pady=(8, 2))

        self.btn_master = tk.Button(btn_row, text="▶ START AUTOMATION LOOP", font=("Segoe UI", 10, "bold"),
                                    bg=self.accent_green, fg="#11111b", activebackground="#88c983",
                                    relief="flat", padx=18, pady=8, cursor="hand2", command=self._start_automation)
        self.btn_master.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_stop = tk.Button(btn_row, text="🛑 STOP ALL COMMANDS", font=("Segoe UI", 10, "bold"),
                                  bg=self.accent_red, fg="#ffffff", activebackground="#cf6679",
                                  relief="flat", padx=18, pady=8, cursor="hand2", command=self._stop_all)
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 10))

        btn_m_collect = tk.Button(btn_row, text="⚡ Master Collect All (1-Shot)", font=("Segoe UI", 10, "bold"),
                                  bg=self.accent_yellow, fg="#11111b", activebackground="#dfc68b",
                                  relief="flat", padx=16, pady=8, cursor="hand2", command=lambda: self._send_cmd("collectall"))
        btn_m_collect.pack(side=tk.LEFT)

        # 3. Quick 1-Click Sector Actions Grid
        grid_frame = tk.Frame(self.tab_dashboard, bg=self.bg_dark)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=4)

        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        # Card 1: Fields & Crops
        c1 = self._create_card(grid_frame, "🌾 Fields & Crops", 0, 0)
        tk.Label(c1, text="Direct memory harvest and replant on active game ticks.", font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card).pack(anchor="w", pady=(0, 6))
        b1 = tk.Button(c1, text="Harvest & Replant Crops Now", bg=self.accent_blue, fg="#11111b", font=("Segoe UI", 9, "bold"),
                       relief="flat", pady=5, cursor="hand2", command=lambda: self._send_cmd("collectcrops"))
        b1.pack(fill=tk.X, pady=2)

        # Card 2: Livestock & Animals
        c2 = self._create_card(grid_frame, "🐔 Livestock & Animals", 0, 1)
        tk.Label(c2, text="Harvest goods (eggs, milk, bacon, wool) and feed pens.", font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card).pack(anchor="w", pady=(0, 6))
        b2_col = tk.Button(c2, text="Collect Animal Products (0x014a7d88)", bg=self.accent_blue, fg="#11111b", font=("Segoe UI", 9, "bold"),
                           relief="flat", pady=5, cursor="hand2", command=lambda: self._send_cmd("collectanimals"))
        b2_col.pack(fill=tk.X, pady=2)
        b2_feed = tk.Button(c2, text="Distribute Feed to Pens (0x014aae28)", bg=self.bg_card_highlight, fg=self.fg_main, font=("Segoe UI", 9),
                            relief="flat", pady=4, cursor="hand2", command=lambda: self._send_cmd("feedanimals"))
        b2_feed.pack(fill=tk.X, pady=2)

        # Card 3: Production Machines
        c3 = self._create_card(grid_frame, "🏭 Production Buildings", 1, 0)
        tk.Label(c3, text="Clear finished goods and restock machine queues.", font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card).pack(anchor="w", pady=(0, 6))
        b3_col = tk.Button(c3, text="Collect Finished Goods (0x014a63f8)", bg=self.accent_blue, fg="#11111b", font=("Segoe UI", 9, "bold"),
                          relief="flat", pady=5, cursor="hand2", command=lambda: self._send_cmd("collectmachines"))
        b3_col.pack(fill=tk.X, pady=2)
        b3_prod = tk.Button(c3, text="Queue Production Recipes (0x014a9cc8)", bg=self.bg_card_highlight, fg=self.fg_main, font=("Segoe UI", 9),
                            relief="flat", pady=4, cursor="hand2", command=lambda: self._send_cmd("producemachines"))
        b3_prod.pack(fill=tk.X, pady=2)

        # Card 4: Orchard & Trees
        c4 = self._create_card(grid_frame, "🍎 Orchard & Bushes", 1, 1)
        tk.Label(c4, text="Harvest apples, cherries, berries & cacao into silo.", font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card).pack(anchor="w", pady=(0, 6))
        b4_fruits = tk.Button(c4, text="Harvest All Orchard Fruits", bg=self.accent_blue, fg="#11111b", font=("Segoe UI", 9, "bold"),
                              relief="flat", pady=5, cursor="hand2", command=lambda: self._send_cmd("collectfruits"))
        b4_fruits.pack(fill=tk.X, pady=2)

    def _create_card(self, parent, title, row, col):
        card = tk.Frame(parent, bg=self.bg_card, padx=14, pady=10, relief="flat",
                        highlightbackground=self.bg_card_highlight, highlightthickness=1)
        card.grid(row=row, column=col, sticky="nsew", padx=6, pady=4)
        lbl = tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), fg=self.fg_main, bg=self.bg_card)
        lbl.pack(anchor="w", pady=(0, 4))
        return card

    def _start_automation(self):
        """Construct selected module list and launch non-blocking master auto."""
        mods = []
        if self.opt_crops.get(): mods.append("crops")
        if self.opt_animals.get(): mods.append("animals")
        if self.opt_feed.get(): mods.append("feed")
        if self.opt_machines.get(): mods.append("machines")
        if self.opt_produce.get(): mods.append("produce")
        if self.opt_fruits.get(): mods.append("fruits")
        if self.opt_sell.get(): mods.append("sell")

        if not mods:
            messagebox.showwarning("No Sectors Selected", "Please select at least one sector above (Crops, Animals, Machines, etc.).")
            return

        delay = self.entry_delay.get().strip() or "130"
        crop_raw = self.crop_var.get().split()[0]

        mod_str = ",".join(mods)
        cmd = f"master start {delay} {crop_raw} {mod_str}"

        self.log(f"[GUI] Starting Custom Automation: {cmd}")
        res = self._send_cmd(cmd)

        if "OK" in res:
            self.running_auto = True
            self.btn_master.config(text="● AUTOMATION RUNNING", bg="#50fa7b")
            self.status_text.config(text=f"Automation Running: {mod_str} (Delay: {delay}s)")
        else:
            self.log(f"[-] Backend response: {res}")

    def _stop_all(self):
        """Send emergency stop to all backend threads immediately."""
        self.log("[GUI] 🛑 EMERGENCY STOP ACTIVATED: Halting all automation loops...")
        res = self._send_cmd("stop")
        self._send_cmd("farm stop")
        self._send_cmd("master stop")
        self.running_auto = False
        self.btn_master.config(text="▶ START AUTOMATION LOOP", bg=self.accent_green)
        self.status_text.config(text="All commands and automation loops STOPPED.")
        self.log(f"[✓] Stopped: {res}")

    def _init_shop_tab(self):
        """Roadside Shop manager: auto-sell with anti-ban pricing and coin collection."""
        container = tk.Frame(self.tab_shop, bg=self.bg_dark)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Card 1: Selling Controls
        sell_card = tk.Frame(container, bg=self.bg_card, padx=16, pady=14, relief="flat",
                             highlightbackground=self.accent_yellow, highlightthickness=1)
        sell_card.pack(fill=tk.X, pady=(0, 10))

        tk.Label(sell_card, text="🏪 ROADSIDE SHOP AUTO-SELLER & PRICING ENGINE", font=("Segoe UI", 12, "bold"),
                 fg=self.accent_yellow, bg=self.bg_card).pack(anchor="w", pady=(0, 2))
        tk.Label(sell_card, text="List items for sale across shop crates with anti-ban humanized pricing and automated ad management.",
                 font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card).pack(anchor="w", pady=(0, 10))

        # Row 1: Item & Slot
        r1 = tk.Frame(sell_card, bg=self.bg_card)
        r1.pack(fill=tk.X, pady=4)

        tk.Label(r1, text="Item to Sell:", font=("Segoe UI", 9, "bold"), fg=self.fg_main, bg=self.bg_card, width=14, anchor="w").pack(side=tk.LEFT)
        self.shop_item_var = tk.StringVar(value="400001 (Wheat)")
        items_list = [
            "400001 (Wheat)", "400002 (Corn)", "400003 (Soybean)", "400004 (Sugarcane)",
            "400005 (Carrot)", "400006 (Indigo)", "400007 (Pumpkin)", "1100015 (Bread)",
            "1100000 (Cream)", "1100001 (Butter)", "1100002 (Cheese)", "1100013 (Brown Sugar)",
            "1800000 (Saw)", "1800001 (Axe)", "1800004 (Bolt)", "1800005 (Plank)", "1800006 (Duct Tape)"
        ]
        combo_item = ttk.Combobox(r1, textvariable=self.shop_item_var, values=items_list, state="readonly", width=22)
        combo_item.pack(side=tk.LEFT, padx=(0, 16))

        tk.Label(r1, text="Target Slot:", font=("Segoe UI", 9, "bold"), fg=self.fg_main, bg=self.bg_card, width=12, anchor="w").pack(side=tk.LEFT)
        self.shop_slot_var = tk.StringVar(value="All Available Slots")
        slots_list = ["All Available Slots", "Slot #0", "Slot #1", "Slot #2", "Slot #3", "Slot #4", "Slot #5", "Slot #6", "Slot #7"]
        combo_slot = ttk.Combobox(r1, textvariable=self.shop_slot_var, values=slots_list, state="readonly", width=18)
        combo_slot.pack(side=tk.LEFT)

        # Row 2: Quantity & Price Mode
        r2 = tk.Frame(sell_card, bg=self.bg_card)
        r2.pack(fill=tk.X, pady=4)

        tk.Label(r2, text="Quantity / Slot:", font=("Segoe UI", 9, "bold"), fg=self.fg_main, bg=self.bg_card, width=14, anchor="w").pack(side=tk.LEFT)
        self.shop_count_var = tk.StringVar(value="10")
        combo_count = ttk.Combobox(r2, textvariable=self.shop_count_var, values=["10 (Max Stack)", "5", "2", "1"], state="readonly", width=22)
        combo_count.pack(side=tk.LEFT, padx=(0, 16))

        tk.Label(r2, text="Price Setting:", font=("Segoe UI", 9, "bold"), fg=self.fg_main, bg=self.bg_card, width=12, anchor="w").pack(side=tk.LEFT)
        self.shop_price_mode_var = tk.StringVar(value="Anti-Ban Max (Human - Safe)")
        price_modes = ["Anti-Ban Max (Human - Safe)", "Absolute Max Price", "Medium (~50% Max)", "Low (1 Coin Quick Dump)", "Custom Price"]
        combo_price = ttk.Combobox(r2, textvariable=self.shop_price_mode_var, values=price_modes, state="readonly", width=24)
        combo_price.pack(side=tk.LEFT, padx=(0, 10))

        # Row 3: Custom Price Entry & Ad Option
        r3 = tk.Frame(sell_card, bg=self.bg_card)
        r3.pack(fill=tk.X, pady=4)

        tk.Label(r3, text="Custom Coins:", font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card, width=14, anchor="w").pack(side=tk.LEFT)
        self.entry_custom_price = tk.Entry(r3, width=8, font=("Consolas", 10), bg=self.bg_dark, fg="#ffffff", insertbackground="#ffffff", relief="flat")
        self.entry_custom_price.pack(side=tk.LEFT, padx=(0, 16), ipady=2)
        self.entry_custom_price.insert(0, "36")

        tk.Label(r3, text="Newspaper Ad:", font=("Segoe UI", 9, "bold"), fg=self.fg_main, bg=self.bg_card, width=12, anchor="w").pack(side=tk.LEFT)
        self.shop_ad_var = tk.StringVar(value="Auto (Respect 5-min Cooldown)")
        ad_choices = ["Auto (Respect 5-min Cooldown)", "Skip Ad (0)", "Force Ad (1)"]
        combo_ad = ttk.Combobox(r3, textvariable=self.shop_ad_var, values=ad_choices, state="readonly", width=24)
        combo_ad.pack(side=tk.LEFT)

        # Action Buttons Row
        btn_row = tk.Frame(sell_card, bg=self.bg_card)
        btn_row.pack(fill=tk.X, pady=(12, 4))

        btn_sell = tk.Button(btn_row, text="🏷️ List & Sell in Roadside Shop", font=("Segoe UI", 10, "bold"),
                             bg=self.accent_green, fg="#11111b", activebackground=self.accent_purple,
                             relief="flat", padx=16, pady=6, cursor="hand2", command=self._execute_shop_sell)
        btn_sell.pack(side=tk.LEFT, padx=(0, 10))

        # Card 2: Revenue Collection & 5-Min Ad Monitor
        col_card = tk.Frame(container, bg=self.bg_card, padx=16, pady=14, relief="flat",
                            highlightbackground=self.accent_blue, highlightthickness=1)
        col_card.pack(fill=tk.X, pady=4)

        tk.Label(col_card, text="💰 REVENUE COLLECTION & AD TIMER MONITOR", font=("Segoe UI", 11, "bold"),
                 fg=self.accent_blue, bg=self.bg_card).pack(anchor="w", pady=(0, 2))
        tk.Label(col_card, text="Collect all coins from sold crates into your farm balance with 1 click. Monitor the 5-minute newspaper ad timer.",
                 font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card).pack(anchor="w", pady=(0, 8))

        c_row = tk.Frame(col_card, bg=self.bg_card)
        c_row.pack(fill=tk.X, pady=4)

        btn_collect_coins = tk.Button(c_row, text="💰 Collect All Store Coins Now", font=("Segoe UI", 10, "bold"),
                                      bg=self.accent_blue, fg="#11111b", activebackground="#74c7ec",
                                      relief="flat", padx=16, pady=6, cursor="hand2", command=lambda: self._send_cmd("collectcoins 10"))
        btn_collect_coins.pack(side=tk.LEFT, padx=(0, 12))

        btn_check_ad = tk.Button(c_row, text="📰 Check 5-Min Ad Cooldown", font=("Segoe UI", 9),
                                 bg=self.bg_card_highlight, fg=self.fg_main, activebackground=self.bg_dark,
                                 relief="flat", padx=12, pady=6, cursor="hand2", command=lambda: self._send_cmd("adstatus"))
        btn_check_ad.pack(side=tk.LEFT)

    def _execute_shop_sell(self):
        item_id = self.shop_item_var.get().split()[0]
        slot_raw = self.shop_slot_var.get()
        slot = "all" if "all" in slot_raw.lower() else slot_raw.split("#")[-1]
        count = self.shop_count_var.get().split()[0]
        mode_raw = self.shop_price_mode_var.get()

        if "anti-ban" in mode_raw.lower() or "safe" in mode_raw.lower():
            mode = "antibank"
        elif "max" in mode_raw.lower():
            mode = "max"
        elif "medium" in mode_raw.lower():
            mode = "medium"
        elif "low" in mode_raw.lower():
            mode = "low"
        else:
            mode = self.entry_custom_price.get().strip() or "36"

        ad_raw = self.shop_ad_var.get()
        if "skip" in ad_raw.lower() or "(0)" in ad_raw:
            ad = "0"
        elif "force" in ad_raw.lower() or "(1)" in ad_raw:
            ad = "1"
        else:
            ad = "auto"

        cmd = f"shopsell {item_id} {slot} {count} {mode} {ad}"
        self.log(f"[GUI] Executing Roadside Shop Sell: {cmd}")
        res = self._send_cmd(cmd)
        messagebox.showinfo("Shop Sale Dispatched", f"Result: {res}")

    def _init_teleport_tab(self):
        """Instant screen jump / camera teleport navigator."""
        container = tk.Frame(self.tab_teleport, bg=self.bg_dark)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        nav_card = tk.Frame(container, bg=self.bg_card, padx=16, pady=14, relief="flat",
                            highlightbackground=self.accent_purple, highlightthickness=1)
        nav_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(nav_card, text="🚀 INSTANT SCREEN JUMP & CAMERA TELEPORT", font=("Segoe UI", 12, "bold"),
                 fg=self.accent_purple, bg=self.bg_card).pack(anchor="w", pady=(0, 2))
        tk.Label(nav_card, text="Instantly position the game screen at any farm landmark or custom coordinate with zero lag.",
                 font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card).pack(anchor="w", pady=(0, 14))

        # Landmark Quick-Buttons Grid
        grid = tk.Frame(nav_card, bg=self.bg_card)
        grid.pack(fill=tk.X, pady=6)

        landmarks = [
            ("🏡 Farmhouse & Silo Center", "farm", self.accent_blue),
            ("🏪 Roadside Shop & Mailbox", "shop", self.accent_yellow),
            ("🐔 Livestock Pens & Pastures", "animals", self.accent_green),
            ("🏭 Machine Factories & Bakery", "machines", self.accent_purple),
            ("⛏️ The Mountain Mine", "mine", "#fab387"),
            ("🚢 River Fishing Boat & Docks", "boat", "#89dceb"),
            ("🚂 Town Train Station", "town", "#f5c2e7"),
        ]

        for i, (title, target, color) in enumerate(landmarks):
            r, c = divmod(i, 2)
            btn = tk.Button(grid, text=title, font=("Segoe UI", 10, "bold"), bg=color, fg="#11111b",
                            relief="flat", padx=16, pady=10, cursor="hand2",
                            command=lambda t=target: self._send_cmd(f"jump {t}"))
            btn.grid(row=r, column=c, padx=8, pady=6, sticky="ew")

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        # Custom Coordinate Panning
        cust_card = tk.Frame(nav_card, bg=self.bg_card_highlight, padx=12, pady=10)
        cust_card.pack(fill=tk.X, pady=(16, 4))

        tk.Label(cust_card, text="Manual Coordinate Jump (dx, dy pixels):", font=("Segoe UI", 9, "bold"),
                 fg=self.fg_main, bg=self.bg_card_highlight).pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(cust_card, text="X:", font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card_highlight).pack(side=tk.LEFT)
        self.entry_jump_x = tk.Entry(cust_card, width=6, font=("Consolas", 10), bg=self.bg_dark, fg="#ffffff", insertbackground="#ffffff", relief="flat")
        self.entry_jump_x.pack(side=tk.LEFT, padx=4)
        self.entry_jump_x.insert(0, "300")

        tk.Label(cust_card, text="Y:", font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card_highlight).pack(side=tk.LEFT, padx=(6, 0))
        self.entry_jump_y = tk.Entry(cust_card, width=6, font=("Consolas", 10), bg=self.bg_dark, fg="#ffffff", insertbackground="#ffffff", relief="flat")
        self.entry_jump_y.pack(side=tk.LEFT, padx=4)
        self.entry_jump_y.insert(0, "300")

        btn_jump_custom = tk.Button(cust_card, text="Pan Camera", font=("Segoe UI", 9, "bold"),
                                    bg=self.accent_purple, fg="#11111b", relief="flat", padx=10, pady=2, cursor="hand2",
                                    command=lambda: self._send_cmd(f"jump {self.entry_jump_x.get()} {self.entry_jump_y.get()}"))
        btn_jump_custom.pack(side=tk.LEFT, padx=12)

    def _init_builder_tab(self):
        builder_box = tk.Frame(self.tab_builder, bg=self.bg_card, padx=20, pady=16, relief="flat",
                               highlightbackground=self.bg_card_highlight, highlightthickness=1)
        builder_box.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        tk.Label(builder_box, text="⚡ Universal ARM64 Memory Command Builder", font=("Segoe UI", 13, "bold"),
                 fg=self.accent_yellow, bg=self.bg_card).pack(anchor="w")

        tk.Label(builder_box, text="Execute ANY real-time LogicCommand directly in Hay Day's native game memory. Select a captured template or enter raw vtables.",
                 font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card).pack(anchor="w", pady=(2, 14))

        # Preset selector
        preset_frame = tk.Frame(builder_box, bg=self.bg_card)
        preset_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(preset_frame, text="Command Preset:", font=("Segoe UI", 10, "bold"), fg=self.fg_main, bg=self.bg_card, width=16, anchor="w").pack(side=tk.LEFT)
        self.preset_var = tk.StringVar(value=list(CAPTURED_COMMANDS.keys())[0])
        preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var, values=list(CAPTURED_COMMANDS.keys()), state="readonly", width=40)
        preset_combo.pack(side=tk.LEFT, padx=6)
        preset_combo.bind("<<ComboboxSelected>>", self._on_preset_change)

        self.preset_desc_lbl = tk.Label(builder_box, text=CAPTURED_COMMANDS[list(CAPTURED_COMMANDS.keys())[0]]["desc"],
                                        font=("Segoe UI", 9, "italic"), fg=self.accent_blue, bg=self.bg_card)
        self.preset_desc_lbl.pack(anchor="w", pady=(0, 12))

        # Field 1: Vtable Offset
        f1 = tk.Frame(builder_box, bg=self.bg_card)
        f1.pack(fill=tk.X, pady=4)
        tk.Label(f1, text="Vtable Offset (Hex):", font=("Segoe UI", 10), fg=self.fg_main, bg=self.bg_card, width=16, anchor="w").pack(side=tk.LEFT)
        self.entry_vtable = tk.Entry(f1, font=("Consolas", 10), bg=self.bg_dark, fg="#ffffff", insertbackground="#ffffff", relief="flat", width=30)
        self.entry_vtable.pack(side=tk.LEFT, padx=6, ipady=3)
        self.entry_vtable.insert(0, "0x014aae28")

        # Field 2: Target ID (+24)
        f2 = tk.Frame(builder_box, bg=self.bg_card)
        f2.pack(fill=tk.X, pady=4)
        self.lbl_target = tk.Label(f2, text="Animal ID (+24):", font=("Segoe UI", 10), fg=self.fg_main, bg=self.bg_card, width=16, anchor="w")
        self.lbl_target.pack(side=tk.LEFT)
        self.entry_target = tk.Entry(f2, font=("Consolas", 10), bg=self.bg_dark, fg="#ffffff", insertbackground="#ffffff", relief="flat", width=30)
        self.entry_target.pack(side=tk.LEFT, padx=6, ipady=3)
        self.entry_target.insert(0, "2300002")

        # Field 3: Param 2 (+28)
        f3 = tk.Frame(builder_box, bg=self.bg_card)
        f3.pack(fill=tk.X, pady=4)
        self.lbl_param = tk.Label(f3, text="Feed ID (+28):", font=("Segoe UI", 10), fg=self.fg_main, bg=self.bg_card, width=16, anchor="w")
        self.lbl_param.pack(side=tk.LEFT)
        self.entry_param = tk.Entry(f3, font=("Consolas", 10), bg=self.bg_dark, fg="#ffffff", insertbackground="#ffffff", relief="flat", width=30)
        self.entry_param.pack(side=tk.LEFT, padx=6, ipady=3)
        self.entry_param.insert(0, "600002")

        # Action Buttons
        btn_bar = tk.Frame(builder_box, bg=self.bg_card)
        btn_bar.pack(fill=tk.X, pady=(16, 12))

        btn_run = tk.Button(btn_bar, text="⚡ Inject & Execute Command in Game", font=("Segoe UI", 10, "bold"),
                            bg=self.accent_green, fg="#11111b", activebackground="#88c983",
                            relief="flat", padx=18, pady=8, cursor="hand2", command=self._execute_custom_cmd)
        btn_run.pack(side=tk.LEFT, padx=(0, 10))

        btn_capture = tk.Button(btn_bar, text="📡 Capture Live Commands (60s)", font=("Segoe UI", 9, "bold"),
                                bg=self.bg_card_highlight, fg=self.accent_yellow, activebackground="#45475a",
                                relief="flat", padx=12, pady=8, cursor="hand2", command=lambda: self._send_cmd("capture 60"))
        btn_capture.pack(side=tk.LEFT)

        # Output / Results Box
        tk.Label(builder_box, text="Execution Response:", font=("Segoe UI", 9, "bold"), fg=self.fg_sub, bg=self.bg_card).pack(anchor="w", pady=(10, 2))
        self.txt_builder_out = tk.Text(builder_box, height=8, font=("Consolas", 9), bg=self.bg_dark, fg=self.accent_green,
                                       relief="flat", padx=8, pady=6)
        self.txt_builder_out.pack(fill=tk.BOTH, expand=True)

    def _on_preset_change(self, event=None):
        name = self.preset_var.get()
        if name in CAPTURED_COMMANDS:
            data = CAPTURED_COMMANDS[name]
            self.preset_desc_lbl.config(text=data["desc"])
            self.lbl_target.config(text=data["target_label"] + ":")
            self.lbl_param.config(text=data["param_label"] + ":")

            self.entry_vtable.delete(0, tk.END)
            self.entry_vtable.insert(0, data["vtable"])

            self.entry_target.delete(0, tk.END)
            self.entry_target.insert(0, data["default_target"])

            self.entry_param.delete(0, tk.END)
            self.entry_param.insert(0, data["default_param"])

    def _execute_custom_cmd(self):
        vtable = self.entry_vtable.get().strip()
        target = self.entry_target.get().strip()
        param = self.entry_param.get().strip() or "0"

        if not vtable or not target:
            messagebox.showwarning("Missing Fields", "Please specify both Vtable Offset and Target ID.")
            return

        cmd = f"execcmd {vtable} {target} {param}"
        self.log(f"[GUI] Executing Custom Command: {cmd}")
        res = self._send_cmd(cmd)
        self.txt_builder_out.insert(tk.END, f">> {cmd}\n<< {res}\n\n")
        self.txt_builder_out.see(tk.END)

    def _init_id_finder_tab(self):
        id_box = tk.Frame(self.tab_id_finder, bg=self.bg_card, padx=20, pady=16, relief="flat",
                          highlightbackground=self.bg_card_highlight, highlightthickness=1)
        id_box.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        tk.Label(id_box, text="🔍 Instant Hay Day ID Code Searcher", font=("Segoe UI", 13, "bold"),
                 fg=self.accent_green, bg=self.bg_card).pack(anchor="w")

        tk.Label(id_box, text="Search any Crop, Feed, Good, Building, Machine, Animal or Tool to get its exact Titan Global ID.",
                 font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card).pack(anchor="w", pady=(2, 10))

        # Search bar
        search_frame = tk.Frame(id_box, bg=self.bg_card)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(search_frame, text="Search Item / ID:", font=("Segoe UI", 10, "bold"), fg=self.fg_main, bg=self.bg_card).pack(side=tk.LEFT, padx=(0, 8))
        self.id_search_var = tk.StringVar()
        self.entry_id_search = tk.Entry(search_frame, textvariable=self.id_search_var, font=("Consolas", 10),
                                        bg=self.bg_dark, fg="#ffffff", insertbackground="#ffffff", relief="flat", width=35)
        self.entry_id_search.pack(side=tk.LEFT, padx=(0, 10), ipady=3)
        self.entry_id_search.bind("<KeyRelease>", lambda e: self._perform_id_search())

        # Category quick filter buttons
        cat_bar = tk.Frame(id_box, bg=self.bg_card)
        cat_bar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(cat_bar, text="Quick Filters:", font=("Segoe UI", 9, "bold"), fg=self.fg_sub, bg=self.bg_card).pack(side=tk.LEFT, padx=(0, 6))
        for cat_label, query in [("All", ""), ("🌾 Crops", "crop"), ("🐔 Animals", "chicken"), ("🥣 Feeds", "feed"), ("🍞 Goods", "bread"), ("🏭 Machines", "mill"), ("🪓 Tools", "saw")]:
            btn = tk.Button(cat_bar, text=cat_label, font=("Segoe UI", 8), bg=self.bg_card_highlight, fg=self.fg_main,
                            relief="flat", padx=8, pady=2, cursor="hand2", command=lambda q=query: self._set_id_search(q))
            btn.pack(side=tk.LEFT, padx=2)

        # Treeview / List table
        tree_frame = tk.Frame(id_box, bg=self.bg_dark)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=4)

        columns = ("id", "name", "category")
        self.id_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        self.id_tree.heading("id", text="Global ID")
        self.id_tree.heading("name", text="Item / Entity Name")
        self.id_tree.heading("category", text="Category")

        self.id_tree.column("id", width=120, anchor="center")
        self.id_tree.column("name", width=340, anchor="w")
        self.id_tree.column("category", width=280, anchor="w")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.id_tree.yview)
        self.id_tree.configure(yscroll=scrollbar.set)

        self.id_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Action bar under treeview
        action_bar = tk.Frame(id_box, bg=self.bg_card)
        action_bar.pack(fill=tk.X, pady=(10, 0))

        btn_use_target = tk.Button(action_bar, text="📋 Send to Command Builder (as Target ID)", font=("Segoe UI", 9, "bold"),
                                   bg=self.accent_blue, fg="#11111b", relief="flat", padx=12, pady=5, cursor="hand2",
                                   command=self._use_selected_id_as_target)
        btn_use_target.pack(side=tk.LEFT, padx=(0, 10))

        btn_use_param = tk.Button(action_bar, text="📋 Send to Command Builder (as Secondary Param)", font=("Segoe UI", 9),
                                  bg=self.bg_card_highlight, fg=self.fg_main, relief="flat", padx=12, pady=5, cursor="hand2",
                                  command=self._use_selected_id_as_param)
        btn_use_param.pack(side=tk.LEFT)

        self.lbl_id_count = tk.Label(action_bar, text="", font=("Segoe UI", 9), fg=self.fg_sub, bg=self.bg_card)
        self.lbl_id_count.pack(side=tk.RIGHT)

        # Populate initial list
        self._perform_id_search()

    def _set_id_search(self, q):
        self.id_search_var.set(q)
        self._perform_id_search()

    def _perform_id_search(self):
        q = self.id_search_var.get().strip()
        for row in self.id_tree.get_children():
            self.id_tree.delete(row)

        matches = search_id(q) if q else []
        if not q:
            # Show all
            for cat_name, items in ALL_CATEGORIES.items():
                for item_id, item_name in items.items():
                    matches.append((item_id, item_name, cat_name))

        for item_id, name, cat in matches:
            self.id_tree.insert("", tk.END, values=(item_id, name, cat))

        self.lbl_id_count.config(text=f"Showing {len(matches)} item(s)")

    def _use_selected_id_as_target(self):
        selected = self.id_tree.selection()
        if not selected:
            messagebox.showinfo("Select an Item", "Please click on an item in the list first.")
            return
        item_vals = self.id_tree.item(selected[0])["values"]
        item_id = str(item_vals[0])
        self.entry_target.delete(0, tk.END)
        self.entry_target.insert(0, item_id)
        self.notebook.select(self.tab_builder)
        self.log(f"[ID Finder] Sent ID {item_id} ({item_vals[1]}) to Custom Command Builder as Target ID.")

    def _use_selected_id_as_param(self):
        selected = self.id_tree.selection()
        if not selected:
            messagebox.showinfo("Select an Item", "Please click on an item in the list first.")
            return
        item_vals = self.id_tree.item(selected[0])["values"]
        item_id = str(item_vals[0])
        self.entry_param.delete(0, tk.END)
        self.entry_param.insert(0, item_id)
        self.notebook.select(self.tab_builder)
        self.log(f"[ID Finder] Sent ID {item_id} ({item_vals[1]}) to Custom Command Builder as Secondary Param.")

    def _init_logs_tab(self):
        log_box = tk.Frame(self.tab_logs, bg=self.bg_dark)
        log_box.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Text stream
        self.txt_logs = scrolledtext.ScrolledText(log_box, font=("Consolas", 9), bg=self.bg_card, fg="#cdd6f4",
                                                  insertbackground="#ffffff", relief="flat", padx=10, pady=8)
        self.txt_logs.pack(fill=tk.BOTH, expand=True)

        # Bottom command input
        cmd_bar = tk.Frame(log_box, bg=self.bg_dark, pady=8)
        cmd_bar.pack(fill=tk.X)

        tk.Label(cmd_bar, text="Console Command:", font=("Segoe UI", 9, "bold"), fg=self.fg_main, bg=self.bg_dark).pack(side=tk.LEFT, padx=(0, 6))
        self.entry_raw_cmd = tk.Entry(cmd_bar, font=("Consolas", 10), bg=self.bg_card, fg="#ffffff",
                                      insertbackground="#ffffff", relief="flat")
        self.entry_raw_cmd.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=3)
        self.entry_raw_cmd.bind("<Return>", lambda e: self._send_raw_cmd())

        btn_send = tk.Button(cmd_bar, text="Send", font=("Segoe UI", 9, "bold"), bg=self.accent_blue, fg="#11111b",
                             relief="flat", padx=14, pady=3, cursor="hand2", command=self._send_raw_cmd)
        btn_send.pack(side=tk.LEFT, padx=2)

        btn_clear = tk.Button(cmd_bar, text="Clear", font=("Segoe UI", 9), bg=self.bg_card_highlight, fg=self.fg_main,
                              relief="flat", padx=10, pady=3, cursor="hand2", command=lambda: self.txt_logs.delete("1.0", tk.END))
        btn_clear.pack(side=tk.LEFT, padx=2)

    def _init_screenshot_tab(self):
        ss_box = tk.Frame(self.tab_screenshot, bg=self.bg_card, padx=20, pady=16, relief="flat",
                          highlightbackground=self.bg_card_highlight, highlightthickness=1)
        ss_box.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        tk.Label(ss_box, text="📸 Screenshot & Visual Feature Importer", font=("Segoe UI", 13, "bold"),
                 fg=self.accent_purple, bg=self.bg_card).pack(anchor="w")

        desc = ("YES! You can provide screenshots of any feature, design, or layout you want added.\n"
                "Antigravity has direct image analysis capabilities. Save your image into the folder or select it below,\n"
                "and I will implement every button, layout, and control shown in your picture!")
        tk.Label(ss_box, text=desc, font=("Segoe UI", 10), fg=self.fg_sub, bg=self.bg_card, justify=tk.LEFT).pack(anchor="w", pady=(4, 14))

        picker_frame = tk.Frame(ss_box, bg=self.bg_card)
        picker_frame.pack(fill=tk.X, pady=6)

        btn_pick = tk.Button(picker_frame, text="📁 Select Screenshot / Mockup Image", font=("Segoe UI", 10, "bold"),
                             bg=self.accent_blue, fg="#11111b", relief="flat", padx=16, pady=6, cursor="hand2",
                             command=self._pick_screenshot)
        btn_pick.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_ss_path = tk.Label(picker_frame, text="No image selected yet.", font=("Segoe UI", 9, "italic"),
                                    fg=self.fg_sub, bg=self.bg_card)
        self.lbl_ss_path.pack(side=tk.LEFT)

        guide_box = scrolledtext.ScrolledText(ss_box, height=14, font=("Segoe UI", 10), bg=self.bg_dark, fg=self.fg_main,
                                             relief="flat", padx=12, pady=10)
        guide_box.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        guide_content = """HOW TO SUBMIT YOUR SCREENSHOTS TO ANTIGRAVITY:
======================================================
1. TAKE A SCREENSHOT of your game, desired button layout, or feature concept.
2. SAVE IT in this folder (c:\\Users\\Admin\\Desktop\\inxernal-main\\) as:
   - screenshot.png  OR  layout.jpg
   - Or paste the screenshot directly into our chat window!
3. TELL ME:
   "Here is my screenshot, please add the features shown in it."

WHAT HAPPENS NEXT:
- Antigravity uses multi-modal visual inspection to inspect the image.
- We reverse engineer every game element, coordinate, icon, and button in the screenshot.
- We write the exact Python and Tkinter code into gui.py and loader.py to match your picture!
"""
        guide_box.insert(tk.END, guide_content)
        guide_box.config(state=tk.DISABLED)

    def _pick_screenshot(self):
        filepath = filedialog.askopenfilename(
            title="Select Screenshot or UI Mockup",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp"), ("All Files", "*.*")]
        )
        if filepath:
            self.lbl_ss_path.config(text=f"Selected: {os.path.basename(filepath)}", fg=self.accent_green)
            dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_screenshot.png")
            try:
                import shutil
                shutil.copyfile(filepath, dest)
                self.log(f"[✓] Screenshot copied to: {dest}")
                messagebox.showinfo("Screenshot Ready", f"Screenshot saved as 'user_screenshot.png' in project folder!\n\nSimply tell me in chat: 'I saved my screenshot as user_screenshot.png, please add the features from it.'")
            except Exception as e:
                self.log(f"[-] Could not copy screenshot: {e}")

    def _init_help_tab(self):
        help_box = tk.Frame(self.tab_help, bg=self.bg_dark, padx=16, pady=12)
        help_box.pack(fill=tk.BOTH, expand=True)

        guide_text = scrolledtext.ScrolledText(help_box, font=("Segoe UI", 10), bg=self.bg_card, fg="#cdd6f4",
                                               relief="flat", padx=14, pady=12)
        guide_text.pack(fill=tk.BOTH, expand=True)

        content = """📖 COMPREHENSIVE COMMAND & REVERSE ENGINEERING GUIDE
============================================================

1. HOW TO CAPTURE COMMANDS IN LIVE GAMEPLAY:
   - Click 'Capture Live Commands' or type 'capture 60' in the terminal.
   - Switch to your LDPlayer emulator and manually perform the action (e.g. feed an animal, collect bakery bread).
   - Inxernal hooks 'tryToExecuteCommand' and captures all live LogicCommand parameters into memory.

2. COMMAND STRUCTURE IN TITAN ENGINE:
   Every game command allocated in memory follows this struct:
     +0x00: Vtable Pointer (points to the command's virtual method table)
     +0x24: Target ID (The entity being acted upon: Field, Animal, Building)
     +0x28: Parameter 2 (Recipe ID, Feed ID, Count, or Mode)

3. CAPTURED VTABLES IDENTIFIED IN YOUR LOGS:
   - 0x014aae28: FeedAnimalCommand (+24=animalId, +28=feedId, e.g. 600002 Chicken Feed)
   - 0x014a63f8: CollectBuildingProductCommand (+24=buildingId, +28=0)
   - 0x014a7d88: CollectAnimalProductCommand (+24=penId, +28=0)
   - 0x014a9cc8: StartProduceCommand (+24=recipeId, +28=machineId)
   - 0x014aef68: SelectBuildingCommand (+24=buildingId)

4. HOW TO CREATE AND RUN ANY CUSTOM COMMAND:
   Syntax:
     exec_cmd <vtable_hex> <targetId> [param2]

   Examples:
     exec_cmd 0x14aae28 2300002 600002  -> Feeds Chicken #2 with Chicken Feed
     exec_cmd 0x14a63f8 1300082 0       -> Empties Bakery finished goods
     exec_cmd 0x14a9cc8 1100015 1300082 -> Bakes Bread in Bakery

5. HOW TO STOP RUNNING ACTIONS:
   Click the red 'STOP ALL COMMANDS' button, or type 'stop' into the Live Terminal.
"""
        guide_text.insert(tk.END, content)
        guide_text.config(state=tk.DISABLED)

    def _build_status_bar(self):
        status_bar = tk.Frame(self.root, bg="#11111b", padx=12, pady=4)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_text = tk.Label(status_bar, text="Standby. Connecting to backend on 127.0.0.1:31350...",
                                    font=("Segoe UI", 9), fg=self.fg_sub, bg="#11111b")
        self.status_text.pack(side=tk.LEFT)

        dev_lbl = tk.Label(status_bar, text="Inxernal Memory Core v2.0", font=("Segoe UI", 9, "italic"),
                           fg="#6c7086", bg="#11111b")
        dev_lbl.pack(side=tk.RIGHT)

    def log(self, text):
        def _append():
            timestamp = time.strftime("[%H:%M:%S] ")
            self.txt_logs.insert(tk.END, timestamp + text + "\n")
            self.txt_logs.see(tk.END)
        self.root.after(0, _append)

    def _launch_backend(self):
        try:
            self.log("[+] Launching loader.py backend in Standby Mode (waiting for user orders)...")
            # Notice: launched WITHOUT --master-auto or --auto so it remains in STANDBY until user clicks!
            cmd = [sys.executable, "loader.py"]
            self.backend_proc = subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
            self.log(f"[+] Backend launched in Standby Mode (PID: {self.backend_proc.pid})")
            self.status_text.config(text=f"Backend live (PID: {self.backend_proc.pid}). Waiting for your command.")
        except Exception as e:
            self.log(f"[-] Failed to launch backend: {e}")
            messagebox.showerror("Launch Error", str(e))

    def _auto_connect_loop(self):
        while True:
            if not self.connected:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2.0)
                    s.connect((HOST, PORT))
                    self.sock = s
                    self.connected = True
                    self.root.after(0, self._on_connected)
                except Exception:
                    self.connected = False
                    self.root.after(0, self._on_disconnected)
            time.sleep(3.0)

    def _on_connected(self):
        self.status_pill.config(text="● CONNECTED", fg=self.accent_green)
        self.status_text.config(text=f"Connected to backend on {HOST}:{PORT} - Ready for your command")
        self.log(f"[✓] Established TCP Control link to {HOST}:{PORT}")

    def _on_disconnected(self):
        self.status_pill.config(text="● DISCONNECTED", fg=self.accent_red)
        self.status_text.config(text=f"Waiting for backend on {HOST}:{PORT}...")

    def _send_cmd(self, cmd_str):
        if not self.connected or not self.sock:
            # Try to connect immediately
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2.0)
                s.connect((HOST, PORT))
                self.sock = s
                self.connected = True
                self._on_connected()
            except Exception:
                self.log(f"[-] Cannot send '{cmd_str}': Backend not running on {HOST}:{PORT}")
                return "Error: Backend disconnected"

        try:
            self.sock.sendall((cmd_str.strip() + "\n").encode("utf-8"))
            resp = self.sock.recv(4096).decode("utf-8", errors="replace").strip()
            self.log(f">> {cmd_str} -> {resp}")
            return resp
        except Exception as e:
            self.connected = False
            self.sock = None
            self._on_disconnected()
            self.log(f"[-] Send error: {e}")
            return f"Error: {e}"

    def _send_raw_cmd(self):
        cmd = self.entry_raw_cmd.get().strip()
        if not cmd:
            return
        self.entry_raw_cmd.delete(0, tk.END)
        self._send_cmd(cmd)


def main():
    root = tk.Tk()
    app = HayDayBotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
