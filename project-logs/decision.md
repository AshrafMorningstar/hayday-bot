# 🧠 Decision Log

This file records every important design, architectural, or implementation decision made during the project.

---

## Decision: Create a Dedicated `project-logs/` Folder

- **Decided:** Use a dedicated `project-logs/` folder at the workspace root to hold all session logs.
- **Why needed:** The user requested a structured, persistent logging system so the agent always records what it does, why, and how.
- **Alternatives considered:**
  - Storing logs in a hidden `.logs/` folder — rejected because it may be overlooked.
  - Storing logs in the `.agents/` folder — rejected because that folder is for agent config, not session history.
  - Using a single `LOG.md` file — rejected because combining all log types into one file makes it hard to scan.
- **Steps taken:** Reviewed the user's request, identified the four distinct types of information to capture (work, decisions, progress, extras), and mapped each to a dedicated file.
- **Impact:** The agent now maintains four structured log files that persist across all sessions and provide a full history of every task performed.

---

## Decision: Use `trigger: always_on` in the Rule Frontmatter

- **Decided:** Set `trigger: always_on` in the YAML frontmatter of `work-rules.md`.
- **Why needed:** The logging rule must apply to every single task, with no exceptions. Using `always_on` ensures the agent enforces it automatically without needing to be reminded.
- **Alternatives considered:**
  - `trigger: manual` — rejected because it requires the user to invoke the rule explicitly.
  - No frontmatter — rejected because the rule would not be auto-loaded by the Antigravity agent system.
- **Steps taken:** Reviewed the Antigravity customization system documentation to confirm `always_on` is the correct trigger value.
- **Impact:** The rule is now enforced globally on every task in this workspace.

---

## Decision: Auto Mode Activates Quago Blocking Automatically (2026-09-10T18:50)

- **Decided:** When `--auto` is passed, `os.environ.setdefault("NX_QUAGO", "1")` is called inside `run()` before `spawn_inject()`.
- **Why needed:** Running fully autonomously without Quago blocking significantly increases ban risk. Auto mode implies the intent to farm unattended, so Quago blocking is essential.
- **Alternatives considered:**
  - Require the user to also set `NX_QUAGO=1` manually — rejected because it defeats "fully auto".
  - Hard-set `NX_QUAGO=1` unconditionally — rejected in favour of `setdefault` so the user can still override with `NX_QUAGO=0`.
- **Steps taken:** Read the existing `NX_QUAGO` handling in `spawn_inject()` (line 1445) and confirmed `os.environ` is the right injection point.
- **Impact:** Auto mode always loads the Quago probe, enabling blocking of `api.quago.io` uploads.

---

## Decision: Console Stays Open in Auto Mode (2026-09-10T18:50)

- **Decided:** After auto-starting `loadnative` and `nfarm`, the `console_loop()` is still entered normally, keeping the `nxrth>` prompt live.
- **Why needed:** User asked (via question prompt) to keep the console interactive so they can check status or type `quit`.
- **Alternatives considered:** Headless-only mode (no console) — rejected by user preference.
- **Steps taken:** Auto-startup block runs before `console_loop()` inside `run()`; nfarm runs on a daemon thread, console runs on the main thread.
- **Impact:** User can type `nquago status`, `nfields`, `nstate`, etc. at any time during the autonomous farm.

---

## Decision: setup.py Uses stdlib Only (2026-09-10T18:59)

- **Decided:** setup.py uses only Python stdlib (sys, os, subprocess, shutil, re, argparse, pathlib, time).
- **Why needed:** frida is not yet installed when setup.py first runs, so importing it would crash. Setup must work from a bare Python install.
- **Alternatives considered:** Using click/rich for nicer output - rejected (extra dep). Using a batch-only setup - rejected (too limited for device checks).
- **Impact:** setup.py is self-contained and runs on any Python 3.9+ without pip install first.

## Decision: start_auto.bat Delegates to setup.py (2026-09-10T18:59)

- **Decided:** The batch file only finds Python and calls setup.py, keeping all logic in one Python file.
- **Why needed:** Batch has very limited capability for ADB/device checks. Python is far better suited.
- **Alternatives considered:** All-in-one batch - rejected (too fragile). PowerShell-only - rejected (may need policy change to run).
- **Impact:** Batch and PS1 are thin wrappers; all real logic lives in setup.py.

---

## Decision: Eliminate Non-ASCII Unicode in PowerShell Scripts (2026-09-10T20:50)

- **Decided:** Strip all Unicode characters (em-dashes, box-drawing glyphs) from `install.ps1` and use standard ASCII (`-`, `=`, `+`, `|`).
- **Why needed:** PowerShell 5.1 in default Windows code pages (CP1252/ANSI) decodes UTF-8 multi-byte characters such as `\u2014` as byte sequences containing `0x94` (closing double quote), which breaks script parsing and brace blocks.
- **Alternatives considered:** Forcing UTF-8 with BOM on the script file — rejected because standard ASCII guarantees 100% cross-version compatibility across all Windows systems and shells without BOM dependency.
- **Impact:** `install.ps1` parses and executes cleanly in PowerShell 5.1 and 7+ without encoding corruption.

---

## Decision: Autonomous Device Asset Staging via `stage_device.py` (2026-09-10T20:50)

- **Decided:** Implement `stage_device.py` to automatically download, patch, verify, and push required binaries (`libmetrics.so` and `.service`) to `/data/adb/nxrth-assets/`.
- **Why needed:** Previously, missing emulator assets caused setup to abort with manual user instructions ("Push frida-server..."). The user requested fully automated setup ("do it all").
- **Alternatives considered:** Bundling massive 100MB+ binaries in the git repository — rejected because binary blobs bloat repo size. Downloading and applying tested narrow marker patches at runtime is clean and reproducible.
- **Impact:** Eliminates all manual emulator staging steps; zero-touch deployment on any LDPlayer instance.

---

## Decision: Multi-Hash Verification in `VALID_FRIDA_SHA256` (2026-09-10T20:50)

- **Decided:** Update `loader.py` to validate `FRIDA_BIN` against `VALID_FRIDA_SHA256`, which includes both the original author's hash and official verified Frida 17.17.0 release builds.
- **Why needed:** Hardcoding a single private build hash prevented anyone from running modern official or patched Frida releases, throwing a blocking `LoaderError`.
- **Alternatives considered:** Disabling hash verification entirely — rejected because verification ensures the staged binary is not corrupted.
- **Impact:** Allows verified modern Frida 17.17.0 x86_64/x86 builds to load safely.

---

## Decision: Dual-Repository Strategy (Private vs Public) (2026-09-10T21:08)

- **Decided:** Split project GitHub presence into two distinct repositories:
  1. **Private Repository (`inxernal-private` / `inxernal-core`):** Contains full developer source code, C++ native engine sources, reverse engineering scripts in `tests/`, raw hooks, and in-depth architectural specifications (`README_PRIVATE.md`).
  2. **Public Repository (`inxernal` / `inxernal-public`):** Contains clean, user-facing client tools, automated zero-config setup scripts (`install.bat`, `start_auto.bat`, `setup.py`, `stage_device.py`), precompiled native engine, configuration templates, and an ultra-friendly Quick Start guide (`README.md`).
- **Why needed:** The user explicitly requested both a private and a public repository with complete, easy-to-understand instructions on how to use them fully automatically.
- **Alternatives considered:**
  - Single public repository: rejected because reverse engineering internals and tests can attract unwanted exposure or clutter for general users.
  - Single private repository: rejected because user specifically requested a public repository as well.
- **Steps taken:** Designed clear boundaries for public distribution vs private core development, ensuring both include complete documentation tailored to their respective audiences.
- **Impact:** Clear separation of concerns, secure internal codebase, and approachable public user interface.

---

## Decision: Exclude 100MB+ Binaries via `.gitignore` (2026-09-10T21:08)

- **Decided:** Add `frida_server_x86_64` (111.5 MB) and `gadget_raw.so` to `.gitignore`.
- **Why needed:** GitHub enforces a strict 100.00 MB maximum file size limit. Any commit containing `frida_server_x86_64` will be immediately rejected upon `git push`. Moreover, `stage_device.py` dynamically downloads, patches, and stages these binaries on demand, making repository bloat unnecessary.
- **Alternatives considered:**
  - Using Git LFS (Large File Storage): rejected because Git LFS has strict bandwidth and storage quotas, requires extra user tool setup, and is redundant when `stage_device.py` already provisions binaries automatically.
- **Impact:** Repositories remain lightweight, fast to clone, and free of GitHub rejection errors.

---

## Decision: Full Farm Automation Commands & Master Loop Architecture (2026-09-10T21:16)

- **Decided:** Implement granular per-sector collection commands (`collect_crops`, `collect_animals`, `feed_animals`, `collect_machines`, `produce_machines`, `collect_fruits`), compose them into a unified `collect_all` master harvest command, and provide a persistent unattended loop `master_auto` with human-like jitter.
- **Why needed:** The user requested dedicated individual commands for each farm entity (animals, crops, fruits, machines, feeding) and a master command that executes the entire farm collection fully automatically.
- **Alternatives considered:**
  - Hardcoding everything into a single monolithic script: rejected because players often want to trigger only specific tasks (e.g., only collect animals or only harvest fields) without running the entire loop.
  - Relying exclusively on external screen clicking/OCR: rejected because internal memory execution and hook structures provide 100% reliable execution regardless of screen resolution, occlusion, or window position.
- **Steps taken:**
  1. Identified each game farm entity class and created distinct methods in `NXRTHConsole`.
  2. Built unified orchestration in `cmd_collect_all` and autonomous cycle logic in `cmd_master_auto`.
  3. Integrated all commands into console loop map, help screen, socket server protocol, and CLI parser.
  4. Added `--master-auto` flag across `loader.py`, `setup.py`, and `start_auto.ps1`.
- **Impact:** Complete farm lifecycle automation available both interactively in the CLI, over TCP control socket, and via unattended batch launch.

---

## Decision: Public Repository Naming as `hayday-bot` for Maximum Viral SEO (2026-09-10T21:28)

- **Decided:** Name the public repository `hayday-bot` (instead of generic `inxernal`) and tag it with 14 high-volume gaming automation topics on GitHub.
- **Why needed:** The user explicitly commanded: *"make this repository fully viral and also easy to command I give you full authority and also the Readme.md It was good supervisor and also it was easy to search in the google search result and also every other search engine make it easy to search So give it the very easy name I can Get it more famous so I can get more star"*. `hayday-bot` is the exact #1 keyword combination entered by users on Google, GitHub Search, and YouTube when searching for game bots.
- **Alternatives considered:**
  - Keeping `inxernal`: rejected because nobody searches "inxernal" unless they already know the branding; discoverability would be near zero.
  - Using `supercell-bot`: rejected because it is too broad and dilutes focus on Hay Day.
---

## Decision: Universal ARM64 Code Cave for Arbitrary LogicCommand Execution (2026-09-10T22:15)

- **Decided:** Implement `_build_universal_cave` in ARM64 machine code that dynamically instantiates a 0x48-byte `LogicCommand` via `operator new`, sets the target virtual method table pointer (`vtable_abs`), populates `+0x24` (target ID) and `+0x28` (secondary param), and submits it to `tryToExecuteCommand(gameMode, cmd, 0)`.
- **Why needed:** Analysis of the user's 24 captured commands showed that Hay Day executes every game action (harvesting, feeding, producing, collecting) as a polymorphic `LogicCommand` subclass. Rather than writing separate native hooks for each action, a universal command gate can execute ANY command in the Titan engine.
- **Alternatives considered:**
  - Using Frida's `Memory.alloc` and JavaScript RPC: rejected because JavaScript RPC calls from the host have noticeable latency, cannot run safely inside the game tick thread without causing frame drops or crashes, and don't work reliably when Frida detaches.
  - Relying on screen touch automation: rejected because touches fail when screens scroll or UI elements are covered.
- **Steps taken:** Reverse engineered the exact `LogicCommand` memory layout from the captured logs, synthesized the ARM64 assembly routine, wrote tests in `test_farm_commands.py`, and validated 100% test pass.
- **Impact:** Any captured vtable and parameters can now be executed instantly with `exec_cmd <vtable> <targetId> [param2]`.

---

## Decision: Build GUI with Standard Library Tkinter (2026-09-10T22:15)

- **Decided:** Build `gui.py` using Python's built-in `tkinter` library, styled with a modern dark theme and connected via TCP socket to `loader.py:31350`.
- **Why needed:** The user asked whether this program can be made into a GUI and how to create it. Using `tkinter` eliminates any external pip dependencies (like PyQt6, PySide6, or Electron) which could fail to install on restricted Windows environments.
- **Alternatives considered:**
  - Web UI (React/Vue/Next.js): rejected because a desktop automation tool is much faster and simpler as a single native window without Node.js web server overhead.
  - PyQt6 / CustomTkinter: rejected because they require separate pip downloads, whereas standard `tkinter` comes pre-bundled with Windows Python and works immediately on double-click.
---

## Decision: Launch Backend in Standby Mode by Default (2026-09-10T23:05)

- **Decided:** Launch `loader.py` in Standby Mode (without `--master-auto` or `--auto` flags) when triggered from the GUI, and require the user to explicitly click "Start Automation" after selecting desired sectors.
- **Why needed:** The user reported that starting the GUI was immediately launching the auto-farming loop without giving them a choice of what to do or an option to stop.
- **Alternatives considered:**
  - Asking the user via a modal dialog at launcher startup: rejected because checkboxes in the GUI dashboard provide a more flexible, non-blocking interface.
- **Steps taken:** Removed `--master-auto` from `_launch_backend` in `gui.py`, built the sector options panel, added `self._master_stop` in `loader.py`, and added `stop` / `master start` / `master stop` socket commands.
- **Impact:** The bot never acts on game memory upon launch until the user explicitly selects options and commands it to run. Emergency stop halts actions at any point.

## Decision: Build Master Global ID Catalog & In-GUI Searcher (2026-09-10T23:40)

- **Decided:** Create a dedicated module `game_ids.py` cataloging the Titan Global ID system across all classes (4, 6, 11, 13, 18, 23) and integrate an interactive Treeview search tab into `gui.py`.
- **Why needed:** The user asked how to get all ID codes of everything in the game. Explaining the mathematical formula alone is insufficient; providing a searchable reference directly in the CLI and GUI lets the user look up any item instantly and pipe it into custom commands with 1 click.
- **Alternatives considered:**
  - Dumping raw APK CSV files to disk: rejected because raw CSV files contain hundreds of internal engine rows that are confusing to read without mapping to Global IDs.
- **Steps taken:** Cataloged all known items into structured dictionaries, built bidirectional search functions (by substring name and by ID), and connected them to the GUI Treeview with "Send to Command Builder" buttons.
- **Impact:** Users can search and send any ID to the memory injection builder without manual transcription.

---

## Decision: Author Universal Text Guide and Push to Remote Repositories (2026-09-10T23:55)

- **Decided:** Create `ALL_IDS_AND_COMMANDS_GUIDE.txt` formatted in clean, plain-language text and synchronize it immediately to both GitHub repositories (`origin-public` and `origin-private`).
- **Why needed:** The user explicitly commanded: *"Located a text file and upload all this thing which is your created and give it a name to it and make it easy language to anyone can understand it I give you full authority"*. Providing an unpretentious plain-text file allows any player, beginner, or modder to open and read it on any computer or phone without requiring markdown viewers or code editors.
- **Alternatives considered:**
  - Creating a complex PDF: rejected because `.txt` is universally readable, version-controlled cleanly by Git, and searchable directly in the terminal or browser.
- **Steps taken:** Authored `ALL_IDS_AND_COMMANDS_GUIDE.txt`, staged and committed with Git, authenticated with GitHub CLI helper, and pushed to `AshrafMorningstar/hayday-bot` and `AshrafMorningstar/hayday-core-private`.
- **Impact:** Both GitHub repositories now feature a complete beginner's user manual that is accessible to all users.


