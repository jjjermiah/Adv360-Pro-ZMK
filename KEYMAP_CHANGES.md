# Keymap Changes & Instructions

## ⚠️ MANDATORY: Update This File With Every Keymap Change

Whenever you modify the keymap, **you must document the change here** with:
- Date of change
- What was changed
- Why it was changed
- Which layer(s) were affected

---

## Current Keymap Configuration

### Layer Overview
- **Layer 0 (Base)**: Default typing layer with home row mods on F/J
- **Layer 1 (Kp)**: Keypad layer with numpad on right hand
- **Layer 2 (Fn)**: Function keys + Mac shortcuts
- **Layer 3 (Prime)**: Symbol/programming layer
- **Layer 4 (Mod)**: System/Bluetooth/RGB controls

---

## Changes Log

### 2025-11-17: Initial Documentation & Recent Changes

#### ESC/Shift+Alt Key (Base Layer)
- **Changed**: DEL key in left thumb cluster → ESC key with Shift+Alt on hold
- **Behavior**: Tap for ESC, Hold for Shift+Alt combo
- **Location**: Left thumb cluster, second key from left (was DEL)
- **Reason**: Quick ESC access for Vim, Shift+Alt hold for window management/tmux

#### Home Row Mods (Base Layer)
- **Added**: F key → Hold for Left Ctrl, Tap for F
- **Added**: J key → Hold for Right Ctrl, Tap for J
- **Behavior**: `homerow_mods` with 200ms tapping term, tap-preferred flavor
- **Reason**: Enable Ctrl access without leaving home row for Vim/terminal usage

#### Mac Shortcuts (Fn Layer - Layer 2)
Added Mac-specific shortcuts on Fn layer in familiar keyboard positions:
- **A position**: `Mac_SelAll` (Cmd+A) - Select All
- **S position**: `Mac_Save` (Cmd+S) - Save
- **Z position**: `Mac_Undo` (Cmd+Z) - Undo
- **X position**: `Mac_Cut` (Cmd+X) - Cut
- **C position**: `Mac_Copy` (Cmd+C) - Copy
- **V position**: `Mac_Paste` (Cmd+V) - Paste
- **Reason**: Quick access to common Mac shortcuts without complex key combinations

#### Macros Cleanup
- **Removed**: All Windows-specific macros (Win_Cut, Win_Copy, Win_Paste, Win_Undo, Win_Select_All, Win_Desktop, Win_File_Explorer, Win_Snip_Tool, Win_Show_All_Windows, Win_Close_Program, Win_Settings_Menu, Win_Lock_PC, Win_Tile_Left, Win_Tile_Up, Win_Tile_Down, Win_Tile_Right)
- **Kept**: Generic macros (quotes, dquotes, braces, parens, brackets, kinesis)
- **Kept**: All Mac-specific macros
- **Reason**: Mac-only workflow, reduce clutter

#### Formatting
- **Changed**: Aligned all layer bindings for better readability
- **Changed**: Consistent column spacing across all layers
- **Reason**: Easier visual parsing and maintenance

---

## Macro Behaviors Explained

### Auto-Pair Macros
These macros type a pair of delimiters and position the cursor between them:

- **`macro_quotes`**: Types `''` → cursor between single quotes
- **`macro_dquotes`**: Types `""` → cursor between double quotes
- **`macro_braces`**: Types `{}` → cursor between curly braces
- **`macro_parens`**: Types `()` → cursor between parentheses
- **`macro_brackets`**: Types `[]` → cursor between square brackets

**Usage**: Perfect for coding - one keypress gets you paired delimiters ready for input.

### Mac System Macros
Standard Mac shortcuts wrapped as macros for easy keymap assignment:
- Cut, Copy, Paste, Undo, Select All, Save
- Mission Control, Spotlight Search, Screen Snip
- Close Program, Strikethrough Text

---

## Build Instructions

```bash
# Build firmware
make all

# Generate keymap visualization
pixi run generate_keymap
pixi run svg

# Firmware output location
# Left: firmware/*-left-*.uf2
# Right: firmware/*-right-*.uf2
```

---

## Layer Access Keys

- **Layer 1 (Kp)**: Toggle via top-left thumb cluster (tog 1)
- **Layer 2 (Fn)**: Momentary via bottom-left thumb area (mo 2)
- **Layer 3 (Prime)**: Momentary via bottom-right corner (mo 3)
- **Layer 4 (Mod)**: Momentary via top-right thumb cluster (mo 4)

---

## Future Considerations

### Home Row Mods Tuning
If you experience issues with J/F triggering Ctrl accidentally in Neovim:
- Consider adding `require-prior-idle-ms = <150>` to allow key repeat
- May need to adjust `tapping-term-ms` or change flavor to `balanced`
- Current: tap-preferred with 200ms tapping term, 175ms quick-tap

### Potential Additions
- More auto-pair macros for other delimiter types
- Additional Mac system shortcuts
- Custom combos for frequently used sequences
