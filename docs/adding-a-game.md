# Adding a New Game

This guide walks you through adding support for a new 4X strategy game.

## Prerequisites

- The game running on an Android emulator (BlueStacks recommended)
- ADB connected: `adb devices` shows your emulator
- Python 3.9+ with the framework installed: `pip install -e ".[all]"`

## Step 1: Copy the Template

```bash
cp -r games/_template games/my_game
cd games/my_game
```

## Step 2: Map UI Coordinates

Take a screenshot of the game's home screen:
```bash
adb -s emulator-5554 shell screencap -p /sdcard/screen.png
adb -s emulator-5554 pull /sdcard/screen.png ./home_screen.png
```

Open `home_screen.png` in an image editor and note pixel coordinates of:
- Bottom navigation tabs
- Building positions on the city map
- Popup close/confirm/cancel buttons
- Building menu buttons (upgrade, train, etc.)

Edit `coordinate_map.py` with these coordinates.

## Step 3: Define Screen States

Edit `state_machine.py`:
- List all screen states your game has (home, building menu, popups, etc.)
- Define which states are popups that need auto-dismissing
- Write popup handling logic (which button to tap for each popup type)

## Step 4: Write Screen Detection

Edit `screen_analyzer.py`:
- **Fast path**: Pixel-based rules (check colors at fixed positions)
- **Slow path**: OCR-based rules (read text, match patterns)

Tips:
- Bottom navigation bar presence → home screen
- Dark overlay + bright center → popup
- Specific text patterns → specific screens

## Step 5: Add Game Knowledge

Edit `knowledge.py`:
- Building upgrade prerequisites (what's needed for each level)
- Research priorities
- Troop training data
- Daily routine priority list

## Step 6: Write Workflows

Edit `workflow_engine.py` with tap sequences for each task:
- `upgrade_building()`: home → tap building → tap upgrade → confirm
- `train_troops()`: home → tap barracks → tap train → max → confirm
- `collect_resources()`: sweep-tap the base for floating icons
- `alliance_help()`: open alliance tab → help all

Each workflow should:
1. Ensure the bot is on the right screen
2. Execute the tap sequence
3. Verify the action succeeded
4. Return to home screen

## Step 7: Test

```bash
python main.py --test    # Verify ADB + OCR work
python main.py           # Run the bot
```

## Step 8: Submit a PR

If your game works, please contribute it back!
See [CONTRIBUTING.md](../CONTRIBUTING.md) for PR guidelines.

## Tips

- Start with just 3-4 workflows (upgrade, train, collect)
- Add more workflows incrementally as you verify each one works
- Use the reflection log to track what fails and why
- Template matching builds up automatically — the bot learns building positions over time
- The `--test` flag is your best friend during development
