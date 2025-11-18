# TODO List

## Quick Notes

*Jot down your todos here - keep them brief and clear*

- [ ]


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

Add more action plans as needed
