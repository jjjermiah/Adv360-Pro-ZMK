# TODO List

## Quick Notes

*Jot down your todos here - keep them brief and clear*

## Instructions for LLM Assistant

Please review the Quick Notes section below and for each checked item:

1. Create a detailed Action Plan entry with actionable steps
2. Remove the completed item from Quick Notes
3. Add the original quick note text as a "Raw Todo" field in the corresponding Action Plan entry

**Action Plan Template:**

```markdown
### Todo Item: [Descriptive Name]
**Goal:** [Brief description]
**Raw Todo:** [Original quick note text]
**Steps:**
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3
- [ ] Step 4
```




## Action Plan

*LLM-generated detailed plans with actionable steps*

### Todo Item: Update base key at position 58 to `#` / `%` ✅
**Goal:** Change the key currently producing `/` and `?` at physical position 58 so it produces `#` normally and `%` when shifted.
**Raw Todo:** base layer: in position 58 it is currently the '/' and '?' symbol. I want it to be # and % on shift
**Steps:**
- [x] Locate physical index `58` in `assets/key-positions.md` to confirm position mapping.
- [x] Find the corresponding binding in `config/adv360.keymap` under `default_layer` (bindings are listed in physical order).
- [x] Add or use a `behavior-mod-morph` entry (or replace the key) so the unshifted keycode is `HASH` (or `POUND`) and the shifted keycode is `PRCNT` (percent). Use the existing `pl_pctn` pattern as an example.
- [x] Run `pixi run svg` to regenerate the keymap diagram and visually confirm placement.
- [x] Run `make all` and validate the build completes without errors.
- [x] Test on device (flash left then right) or with your normal validation steps.

---

### Todo Item: Move bracket key from 73→74 and set `$`/`@` at 73 ✅
**Goal:** Move the bracket (`[` / `{`) that currently sits at position 73 to position 74 (and remove the old 74 mapping), then set position 73 to produce `$` normally and `@` when shifted.
**Raw Todo:** base layer: in position 73 it is the '['  and '{' i want to move this to 74, and remove 74. in the place of 73 I want '$' and '@'
**Steps:**
- [x] Confirm physical indices `73` and `74` in `assets/key-positions.md` and how they map to the `default_layer` bindings order.
- [x] Edit `config/adv360.keymap` default_layer to swap the binding at 73 into the 74 slot and clear the old 74 slot.
- [x] Set the new 73 binding to a mod-morph or explicit keycode sequence for `$` and `@` (e.g., unshifted `DOLLAR`/`$` and shifted `AT`/`@` — use the ZMK keycodes available in `dt-bindings/zmk/keys.h`).
- [x] Regenerate the keymap diagram with `pixi run svg` and verify layout matches intent.
- [x] Build with `make all` and ensure no compilation errors.
- [x] If any combos or position-based features reference the removed 74 index, update them to use the new index.

---

### Todo Item: Fix Prime layer brackets at positions 8-11 ✅
**Goal:** Ensure `prime` layer positions 8-11 use the opposite bracket characters of what appears in positions 2-5 on that layer (they are currently identical).
**Raw Todo:** prime layer: in positions 8-11 they should be the OPPSOTIE bracket of whats in position   2-5 but theyre the exact same
**Steps:**
- [x] Open `config/adv360.keymap` and locate the `prime` layer bindings.
- [x] Identify which bindings correspond to physical positions 2-5 and 8-11 by counting entries in the bindings block and cross-referencing `assets/key-positions.md`.
- [x] Replace the keycodes at positions 8-11 with the opposite bracket keycodes (e.g., if positions 2-5 are `[` `]` etc., set 8-11 to the matching opposite side and include shifted variants as needed).
- [x] Run `pixi run svg` to confirm the visual mapping.
- [x] Run `make all` and ensure the build succeeds.

---

### Todo Item: Fix quotation key to insert single quote ✅
**Goal:** Change the quote key behavior to insert just one single quote instead of two quotes with cursor positioning.
**Raw Todo:** i hate that the quotation key inserts two by default in position 39, make it just insert one like normal
**Steps:**
- [x] Locate the `quotes_morph` behavior in `config/adv360.keymap` that uses `macro_quotes`.
- [x] Change the binding from `<&macro_quotes>` to `<&kp SQT>` (normal single quote keypress).
- [x] Keep the shifted behavior as `<&kp DQT>` (double quote) for consistency.
- [x] Run `make all` to build and flash the firmware.
- [x] Test that single quote now inserts one character instead of two.

---

### Todo Item: Set position 67 to Alt-Tab
**Goal:** Change key position 67 in the default layer to produce `Alt+Tab` for application switching.
**Raw Todo:** make key position 67 be just 'Alt-Tab'
**Steps:**
- [ ] Locate physical position 67 in `assets/key-positions.md` to confirm it's in the left thumb cluster (third thumb key).
- [ ] Find the corresponding binding in `config/adv360.keymap` under `default_layer` - position 67 is currently `&esc_alt LALT ESC`.
- [ ] Replace with a simple Alt-Tab keycode or create a behavior if needed. Use `&kp LA(TAB)` for the Alt+Tab combination.
- [ ] Regenerate the keymap diagram with `pixi run svg` to verify the visual change.
- [ ] Run `make all` and ensure the build completes without errors.
- [ ] Test on device to confirm Alt-Tab behavior works as expected.

---

### Todo Item: Set position 68 to Cmd-Space (Spotlight)
**Goal:** Change key position 68 in the default layer to produce `Cmd+Space` for macOS Spotlight activation.
**Raw Todo:** and make key position 68 be 'Cmd-Space' (for spotlight)
**Steps:**
- [ ] Locate physical position 68 in `assets/key-positions.md` to confirm it's in the right thumb cluster (first thumb key).
- [ ] Find the corresponding binding in `config/adv360.keymap` under `default_layer` - position 68 is currently `&kp ENTER`.
- [ ] Replace with Cmd+Space keycode: `&kp LG(SPACE)` (Left GUI + Space for macOS Spotlight).
- [ ] Regenerate the keymap diagram with `pixi run svg` to verify the visual change.
- [ ] Run `make all` and ensure the build completes without errors.
- [ ] Test on device to confirm Cmd-Space opens Spotlight.

---

### Todo Item: Set positions 36 and 37 to prime layer switch
**Goal:** Make both positions 36 and 37 activate the prime layer, allowing either hand to access it easily.
**Raw Todo:** make key position 36 and 37 both be the prime mode switch
**Steps:**
- [ ] Locate physical positions 36 and 37 in `assets/key-positions.md` - these are thumb keys (36 is left thumb, 37 is right thumb).
- [ ] Find the current bindings in `config/adv360.keymap` under `default_layer` - position 36 is currently `&kp BSPC` and position 37 is the mod layer switch.
- [ ] Determine the prime layer number by counting layers in the keymap (prime is layer 3 based on the layer order).
- [ ] Replace both bindings with `&mo 3` to momentarily activate the prime layer when held.
- [ ] Consider if you want momentary activation (`&mo`) or toggle (`&tog`) based on usage preference.
- [ ] Regenerate the keymap diagram with `pixi run svg` to verify both positions show the prime layer switch.
- [ ] Run `make all` and ensure the build completes without errors.
- [ ] Test on device to confirm both thumb keys activate the prime layer.

---

Add more action plans as needed
