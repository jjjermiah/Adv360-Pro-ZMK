# Kinesis Advantage 360 Pro ZMK Firmware

## Architecture Overview

This is a **split keyboard firmware** built on ZMK (Zephyr-based Mechanical Keyboard firmware) for the Kinesis Advantage 360 Pro. The codebase uses a **custom ZMK fork** (`refil/zmk` branch `adv360-z3.5-2`) with Advantage 360 Pro-specific features like RGB indicators and layer LEDs.

**Key architectural facts:**
- **Two separate firmware builds**: `adv360_left` and `adv360_right` (left is primary/central, right is peripheral)
- **Device tree-based configuration**: Hardware defined in `.dts`/`.dtsi` files, behaviors and keymaps in `.keymap` files
- **West build system**: Multi-repo tool (defined in `config/west.yml`) that pulls ZMK and Zephyr dependencies
- **Container-based builds**: Docker/Podman container ensures reproducible compilation environment

## File Structure & Responsibilities

```
config/
  adv360.keymap           # Main keymap definition (layers, behaviors, bindings)
  macros.dtsi             # Reusable macro definitions (included in keymap)
  version.dtsi            # Auto-generated version macro (git commit/branch)
  west.yml                # West manifest - defines ZMK fork/revision
  boards/arm/adv360/      # Hardware configuration
    adv360_left_defconfig # Kconfig for left module (BT, RGB, features)
    adv360_right_defconfig # Kconfig for right module
    adv360*.dts           # Device tree hardware definitions
    adv360-layouts.dtsi   # Physical key position mappings
bin/
  build.sh                # Core build script (called by Docker)
  build_all.sh            # Builds both left and right firmwares
firmware/                 # Output directory for .uf2 files
```

## Development Workflow

### Task Management

Follow the workflow and conventions defined in `config/TODO.md`. When the user references todos or tasks, read and follow the instructions in that file for creating detailed action plans from quick notes.

Note: When a user asks to act on todos, ALWAYS read and obey the `config/TODO.md` Action Plan Template (the file is authoritative for how to expand quick notes into step-by-step plans).

### Building Firmware

**After every keymap change:**
1. **Generate keymap visualization:** `pixi run svg` (auto-runs `generate_keymap` if needed)
2. **Build firmware:** `make all`
3. **Validate:** Ensure build completes successfully with no errors

The Makefile automatically:
1. Generates `config/version.dtsi` with git metadata
2. Builds Docker container from `Dockerfile` (cached after first run)
3. Runs `bin/build.sh` inside container via West
4. Outputs timestamped `.uf2` files to `firmware/`
5. Restores `version.dtsi` to prevent git conflicts

### Flashing Process

1. Connect keyboard half to USB
2. Enter bootloader: Press `Mod+macro1` (left) or `Mod+macro3` (right), or use physical reset button
3. Keyboard mounts as USB drive
4. Copy `.uf2` file to drive
5. Keyboard auto-disconnects and reboots with new firmware

**Critical:** Always flash left side first, then right side. Power off both keyboards between flashing operations.

### Keymap Visualization

Uses `keymap-drawer` (Python tool managed by Pixi):
```bash
pixi run generate_keymap  # Parse .keymap → YAML
pixi run svg              # Render YAML → SVG diagram
```

## Keymap Editing Patterns

### ZMK Behavior Syntax

All behaviors in `config/adv360.keymap` follow ZMK's device tree binding format:

**Hold-tap behaviors** (dual-function keys):
```c
behavior_name: hold_tap_label {
    compatible = "zmk,behavior-hold-tap";
    #binding-cells = <2>;               // Takes 2 parameters
    tapping-term-ms = <200>;            // Hold threshold
    quick_tap_ms = <175>;               // Repeat tap window
    flavor = "tap-preferred";           // Tap favored when uncertain
    bindings = <&kp>, <&kp>;            // Hold behavior, Tap behavior
};
```

**Usage in keymap:** `&behavior_name HOLD_PARAM TAP_PARAM`
- Example: `&hm LGUI A` = tap A, hold Left GUI
- Example: `&pipe_shftalt LS(LALT) PIPE` = tap pipe, hold Shift+Alt

**Mod-morph behaviors** (shift-modified keys):
```c
behavior_name: mod_morph_label {
    compatible = "zmk,behavior-mod-morph";
    #binding-cells = <0>;               // Takes no parameters
    bindings = <&kp NORMAL>, <&kp SHIFTED>;
    mods = <(MOD_LSFT|MOD_RSFT)>;      // Trigger mods
};
```

**Macros** (defined in `macros.dtsi`):
```c
macro_name: macro_label {
    compatible = "zmk,behavior-macro";
    #binding-cells = <0>;
    bindings = <&kp KEY1>, <&kp KEY2>;  // Sequence of keypresses
};
```

### Key Position Matrix

Physical key positions documented in `assets/key-positions.md` - required for combos and precise positional features. The keyboard uses a complex matrix due to the split ergonomic layout.

Authoritative Layout: Treat `assets/key-positions.md` and the image at `assets/key-positions.png` as the single source-of-truth for physical key positions. Always refer to these files when adding combos, creating key position mappings, or answering layout questions.

### Layer System

- **32 layers maximum** (ZMK limitation)
- Layer colors defined by layer number (see README table)
- Use `&mo N` for momentary layer activation, `&tog N` for toggle
- `display-name` property sets layer indicator text

## Configuration Patterns

### Feature Toggles (in `adv360_left_defconfig`)

**Enable F13-F24 with NKRO:**
```
CONFIG_ZMK_HID_KEYBOARD_EXTENDED_REPORT=y
```

**Enable BLE battery reporting:**
```
CONFIG_BT_BAS=y
```

**Modify RGB indicator color:**
```
CONFIG_ZMK_RGB_UNDERGLOW_MOD_COLOR=0xFF0000  # Hex RGB
```
(Apply to both `_left_defconfig` and `_right_defconfig`)

### Common Keycodes

- `LG(X)` = Left GUI + X (macOS Cmd+X)
- `LS(LALT)` = Left Shift + Left Alt (simultaneous mods)
- `&kp` = Key press behavior (basic keycode)
- `&mo` = Momentary layer
- `&tog` = Toggle layer

## Troubleshooting

**Build failures after fork update:**
```bash
make clean        # Remove container and firmware
git checkout config/version.dtsi  # Reset auto-generated file
```

**Syntax errors in keymap:**
- Check matching pairs: `<>`, `()`, `{}`
- Verify behavior parameter count matches `#binding-cells`
- Ensure all custom behaviors are defined before keymap section
- Include files must exist: `macros.dtsi`, `version.dtsi`

**West/dependency issues:**
- Check `config/west.yml` for correct ZMK fork revision
- Container rebuild needed if West manifest changes: `make clean_image`

## Beta Testing

To test unreleased ZMK features, edit `config/west.yml`:
```yaml
revision: adv360-z3.5-2  # Change to beta branch name
```

**Warning:** Beta branches may require config repo changes - check for instructions before updating.

## Key Differences from Base ZMK

- **Custom RGB underglow driver** for layer/mod indicators (not in upstream ZMK)
- **Two-module architecture** (left/right) with central/peripheral BT roles
- **Studio RPC** enabled on left module for potential GUI configurator support
- **Pointing device support** enabled (`CONFIG_ZMK_POINTING=y`)
- Uses `CONFIG_ZMK_BEHAVIOR_LOCAL_ID_TYPE_CRC16=y` for behavior identification

Kinesis fork regularly syncs with upstream but isn't always current. Report Kinesis fork issues to ReFil/zmk repo, not upstream ZMK.
