#!/usr/bin/env -S pixi exec --spec python=3.12 --spec typer --spec pydantic -- python
"""Render an Advantage 360 Pro ZMK layer as an ASCII keymap."""

from __future__ import annotations

import re
import sys
from enum import IntEnum
from pathlib import Path
from typing import Annotated

import typer
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

APP = typer.Typer(add_completion=False, no_args_is_help=False)

DEFAULT_KEYMAP = Path("~/.config/Adv360-Pro-ZMK/config/adv360.keymap").expanduser()
BOX_INNER_WIDTH = 6
HALF_GAP = "        "
EXPECTED_KEY_COUNT = 76

KEYS_L: tuple[tuple[int, ...], ...] = (
    (0, 1, 2, 3, 4, 5, 6),
    (14, 15, 16, 17, 18, 19, 20),
    (28, 29, 30, 31, 32, 33, 34),
    (46, 47, 48, 49, 50, 51),
    (60, 61, 62, 63, 64),
)
KEYS_R: tuple[tuple[int, ...], ...] = (
    (7, 8, 9, 10, 11, 12, 13),
    (21, 22, 23, 24, 25, 26, 27),
    (39, 40, 41, 42, 43, 44, 45),
    (54, 55, 56, 57, 58, 59),
    (71, 72, 73, 74, 75),
)
THUMBS_L: tuple[tuple[int, ...], ...] = ((35, 36), (52,), (65, 66, 67))
THUMBS_R: tuple[tuple[int, ...], ...] = ((37, 38), (53,), (68, 69, 70))
TALL_THUMB_POSITIONS = frozenset({65, 66, 69, 70})

MAIN_INDENTS_L = (0, 0, 0, 0, 0)
MAIN_INDENTS_R = (0, 0, 0, 0, 0)

BUILTIN_BINDING_CELLS: dict[str, int] = {
    "bl": 1,
    "bootloader": 0,
    "kp": 1,
    "mkp": 1,
    "mo": 1,
    "none": 0,
    "rgb_ug": 1,
    "studio_unlock": 0,
    "stp": 1,
    "to": 1,
    "tog": 1,
    "trans": 0,
}

BEHAVIOR_ALIASES: dict[str, str] = {
    "alf": "Spot",
    "col_semi": ":/;",
    "dollar_at": "$/@",
    "hash_prcnt": "#/%",
    "macro_kinesis": "Kinesis",
    "macro_ver": "Ver",
    "pl_pctn": "+/%",
    "quo": "'/\"",
    "Mac_Copy": "Copy",
    "Mac_Cut": "Cut",
    "Mac_Paste": "Paste",
    "Mac_Save": "Save",
    "Mac_Select_All": "All",
    "Mac_Undo": "Undo",
}

MOD_LABELS: dict[str, str] = {
    "LALT": "Opt",
    "LCTRL": "Ctl",
    "LGUI": "Cmd",
    "LSHFT": "Sft",
    "RALT": "Opt",
    "RCTRL": "Ctl",
    "RGUI": "Cmd",
    "RSHFT": "Sft",
}

KEY_LABELS: dict[str, str] = {
    "AMPERSAND": "&",
    "AT": "@",
    "BSPC": "Bksp",
    "BKSP": "Bksp",
    "BSLH": "\\",
    "CAPS": "Caps",
    "COLON": ":",
    "COMMA": ",",
    "DEL": "Del",
    "DOT": ".",
    "DOWN": "Down",
    "DQT": '"',
    "DOLLAR": "$",
    "ENTER": "Enter",
    "EQUAL": "=",
    "ESC": "Esc",
    "FSLH": "/",
    "GRAVE": "`",
    "HASH": "#",
    "KP_DIVIDE": "/",
    "KP_DOT": ".",
    "KP_ENTER": "Enter",
    "KP_EQUAL": "=",
    "KP_MINUS": "-",
    "KP_MULTIPLY": "*",
    "KP_NUM": "Num",
    "KP_PLUS": "+",
    "LBKT": "[",
    "LBRC": "{",
    "LEFT": "Left",
    "LEFT_BRACE": "{",
    "LEFT_BRACKET": "[",
    "LEFT_PARENTHESIS": "(",
    "LALT": "Opt",
    "LCTRL": "Ctrl",
    "LGUI": "Cmd",
    "LSHFT": "Shift",
    "MINUS": "-",
    "PG_DN": "PgDn",
    "PG_UP": "PgUp",
    "PIPE": "│",
    "PLUS": "+",
    "PRCNT": "%",
    "RBKT": "]",
    "RBRC": "}",
    "RIGHT": "Right",
    "RIGHT_BRACE": "}",
    "RIGHT_BRACKET": "]",
    "RIGHT_PARENTHESIS": ")",
    "RALT": "Opt",
    "RCTRL": "Ctrl",
    "RGUI": "Cmd",
    "RSHFT": "Shift",
    "SEMI": ";",
    "SEMICOLON": ";",
    "SPACE": "Space",
    "SQT": "'",
    "STAR": "*",
    "TAB": "Tab",
    "UP": "Up",
}


class ExitCode(IntEnum):
    """Stable process exit codes."""

    OK = 0
    RUNTIME_ERROR = 1
    USAGE_ERROR = 2
    DATA_ERROR = 3


class KeymapError(Exception):
    """Domain error with an exit code and safe context for diagnostics."""

    def __init__(
        self,
        message: str,
        *,
        exit_code: ExitCode,
        context: str | None = None,
    ) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.context = context


class BehaviorDef(BaseModel):
    """A ZMK behavior definition relevant to binding parsing and display."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    binding_cells: int = Field(ge=0)
    display_name: str | None = None


class BindingCell(BaseModel):
    """One physical key binding in a ZMK layer."""

    model_config = ConfigDict(frozen=True)

    behavior: str = Field(min_length=1)
    args: tuple[str, ...] = Field(default_factory=tuple)


class LayerDef(BaseModel):
    """A parsed keymap layer with bindings in physical-position order."""

    model_config = ConfigDict(frozen=True)

    node_name: str = Field(min_length=1)
    display_name: str
    bindings: tuple[BindingCell, ...]

    @field_validator("bindings")
    @classmethod
    def validate_binding_count(
        cls,
        bindings: tuple[BindingCell, ...],
    ) -> tuple[BindingCell, ...]:
        """Reject malformed layers before rendering misleading output."""
        if len(bindings) != EXPECTED_KEY_COUNT:
            msg = f"expected {EXPECTED_KEY_COUNT} bindings, found {len(bindings)}"
            raise ValueError(msg)
        return bindings


def read_text(path: Path) -> str:
    """Read UTF-8 text and preserve the failing path in any OSError."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise KeymapError(
            "unable to read keymap file",
            exit_code=ExitCode.USAGE_ERROR,
            context=str(path),
        ) from exc


def strip_comments(source: str) -> str:
    """Remove C-style comments from DTS text before tokenization."""
    without_blocks = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    return re.sub(r"//.*", "", without_blocks)


def load_source_with_local_includes(path: Path) -> str:
    """Load a keymap plus quoted local includes used for custom behaviors."""
    root_text = read_text(path)
    parts = [root_text]
    for include_name in re.findall(r'#include\s+"([^"]+)"', root_text):
        include_path = path.parent / include_name
        if include_path.is_file():
            parts.append(read_text(include_path))
    return "\n".join(parts)


def find_matching_brace(source: str, open_index: int) -> int:
    """Return the matching closing brace for source[open_index]."""
    depth = 0
    for index in range(open_index, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    raise KeymapError(
        "unmatched brace while parsing keymap",
        exit_code=ExitCode.DATA_ERROR,
    )


def find_named_block(source: str, name: str) -> str:
    """Find a named DTS block body by brace matching."""
    match = re.search(rf"\b{re.escape(name)}\s*\{{", source)
    if match is None:
        raise KeymapError(
            f"missing {name} block",
            exit_code=ExitCode.DATA_ERROR,
        )
    open_index = source.find("{", match.start())
    close_index = find_matching_brace(source, open_index)
    return source[open_index + 1 : close_index]


def iter_child_blocks(source: str) -> list[tuple[str, str]]:
    """Return direct child blocks from a DTS block body in source order."""
    children: list[tuple[str, str]] = []
    index = 0
    pattern = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\{")
    while index < len(source):
        match = pattern.search(source, index)
        if match is None:
            break
        open_index = source.find("{", match.start())
        close_index = find_matching_brace(source, open_index)
        children.append((match.group(1), source[open_index + 1 : close_index]))
        index = close_index + 1
    return children


def extract_property_string(body: str, property_name: str) -> str | None:
    """Extract a quoted string DTS property from a block body."""
    match = re.search(rf"\b{re.escape(property_name)}\s*=\s*\"([^\"]+)\"\s*;", body)
    if match is None:
        return None
    return match.group(1)


def extract_binding_cells(body: str) -> int | None:
    """Extract #binding-cells from a behavior body when present."""
    match = re.search(r"#binding-cells\s*=\s*<(\d+)>\s*;", body)
    if match is None:
        return None
    return int(match.group(1))


def parse_behaviors(source: str) -> dict[str, BehaviorDef]:
    """Parse custom behavior labels and their #binding-cells values."""
    behaviors: dict[str, BehaviorDef] = {}
    behavior_pattern = re.compile(
        r"\b([A-Za-z_][A-Za-z0-9_]*)\s*:\s*"
        r"[A-Za-z_][A-Za-z0-9_]*\s*\{(.*?)\n\s*\};",
        flags=re.DOTALL,
    )
    for match in behavior_pattern.finditer(source):
        behavior_name = match.group(1)
        body = match.group(2)
        binding_cells = extract_binding_cells(body)
        if binding_cells is None:
            continue
        display_name = extract_property_string(body, "display-name")
        label_name = extract_property_string(body, "label")
        behaviors[behavior_name] = BehaviorDef(
            name=behavior_name,
            binding_cells=binding_cells,
            display_name=display_name or label_name,
        )
    return behaviors


def tokenize_bindings(binding_body: str) -> list[str]:
    """Split a DTS bindings body into whitespace-delimited tokens."""
    cleaned = strip_comments(binding_body)
    return [token for token in re.split(r"\s+", cleaned.strip()) if token]


def binding_cell_count(
    behavior: str,
    remaining_tokens: list[str],
    behaviors: dict[str, BehaviorDef],
) -> int:
    """Return how many argument tokens follow a behavior invocation."""
    if behavior == "bt":
        return 2 if remaining_tokens and remaining_tokens[0] == "BT_SEL" else 1
    if behavior in behaviors:
        return behaviors[behavior].binding_cells
    if behavior in BUILTIN_BINDING_CELLS:
        return BUILTIN_BINDING_CELLS[behavior]
    return 0


def parse_binding_tokens(
    tokens: list[str],
    behaviors: dict[str, BehaviorDef],
) -> tuple[BindingCell, ...]:
    """Group flat DTS tokens into ZMK binding cells."""
    bindings: list[BindingCell] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if not token.startswith("&"):
            raise KeymapError(
                "expected binding token starting with '&'",
                exit_code=ExitCode.DATA_ERROR,
                context=token,
            )
        behavior = token.removeprefix("&")
        remaining_tokens = tokens[index + 1 :]
        arg_count = binding_cell_count(behavior, remaining_tokens, behaviors)
        args = tuple(remaining_tokens[:arg_count])
        bindings.append(BindingCell(behavior=behavior, args=args))
        index += 1 + arg_count
    return tuple(bindings)


def extract_bindings_body(layer_body: str) -> str:
    """Extract the raw text between a layer's bindings angle brackets."""
    match = re.search(r"\bbindings\s*=\s*<(.*?)>\s*;", layer_body, flags=re.DOTALL)
    if match is None:
        raise KeymapError(
            "selected layer has no bindings property",
            exit_code=ExitCode.DATA_ERROR,
        )
    return match.group(1)


def parse_layers(source: str, behaviors: dict[str, BehaviorDef]) -> list[LayerDef]:
    """Parse all keymap layers in declaration order."""
    keymap_body = find_named_block(source, "keymap")
    layers: list[LayerDef] = []
    for node_name, layer_body in iter_child_blocks(keymap_body):
        if "bindings" not in layer_body:
            continue
        display_name = extract_property_string(layer_body, "display-name") or node_name
        bindings_body = extract_bindings_body(layer_body)
        bindings = parse_binding_tokens(tokenize_bindings(bindings_body), behaviors)
        try:
            layers.append(
                LayerDef(
                    node_name=node_name,
                    display_name=display_name,
                    bindings=bindings,
                )
            )
        except ValidationError as exc:
            raise KeymapError(
                "layer binding count is invalid",
                exit_code=ExitCode.DATA_ERROR,
                context=f"{node_name}: {exc.errors()[0]['msg']}",
            ) from exc
    return layers


def resolve_layer(layers: list[LayerDef], requested_layer: str) -> LayerDef:
    """Resolve a layer by node name or display-name, case-insensitively."""
    requested = requested_layer.casefold()
    for layer in layers:
        if requested in {layer.node_name.casefold(), layer.display_name.casefold()}:
            return layer
    available = ", ".join(f"{layer.display_name} ({layer.node_name})" for layer in layers)
    raise KeymapError(
        "unknown layer",
        exit_code=ExitCode.USAGE_ERROR,
        context=f"requested={requested_layer}; available={available}",
    )


def layer_name_by_index(layers: list[LayerDef], raw_index: str) -> str:
    """Resolve a numeric layer argument to its display name."""
    try:
        layer_index = int(raw_index)
    except ValueError:
        return raw_index
    if layer_index < 0 or layer_index >= len(layers):
        return raw_index
    return layers[layer_index].display_name


def label_keycode(keycode: str) -> str:
    """Return a compact human label for a ZMK keycode token."""
    if re.fullmatch(r"N\d", keycode):
        return keycode.removeprefix("N")
    if re.fullmatch(r"F\d{1,2}", keycode):
        return keycode
    if re.fullmatch(r"KP_N\d", keycode):
        return keycode.removeprefix("KP_N")
    if keycode.startswith("LA(") and keycode.endswith(")"):
        return f"Opt-{label_keycode(keycode[3:-1])}"
    if keycode.startswith("LG(") and keycode.endswith(")"):
        return f"Cmd-{label_keycode(keycode[3:-1])}"
    if keycode.startswith("LS(") and keycode.endswith(")"):
        return f"Sft-{label_keycode(keycode[3:-1])}"
    return KEY_LABELS.get(keycode, keycode.replace("_", " ").title())


def compact_display_name(display_name: str) -> str:
    """Shorten a behavior display-name for a key box."""
    cleaned = display_name.removeprefix("Mac ").replace("Spotlight Search", "Spot")
    words = cleaned.split()
    if not words:
        return display_name
    if len(words) == 1:
        return words[0]
    return "".join(word[0] for word in words)


def label_behavior(
    binding: BindingCell,
    *,
    behaviors: dict[str, BehaviorDef],
    layers: list[LayerDef],
) -> str:
    """Return a compact label for one parsed binding cell."""
    behavior = binding.behavior
    args = binding.args
    if behavior == "kp":
        return label_keycode(args[0]) if args else "kp"
    if behavior in {"hml", "hmr"} and len(args) >= 2:
        return f"{label_keycode(args[1])}/{MOD_LABELS.get(args[0], args[0])}"
    if behavior == "esc_alt" and len(args) >= 2:
        return f"{label_keycode(args[1])}/{MOD_LABELS.get(args[0], args[0])}"
    if behavior == "psa" and len(args) >= 2:
        return f"{label_keycode(args[1])}/Alt"
    if behavior == "fn_save":
        return "SaveFn"
    if behavior == "mo" and args:
        return layer_name_by_index(layers, args[0])
    if behavior == "tog" and args:
        layer_name = layer_name_by_index(layers, args[0])
        layer_name = "KP" if layer_name.casefold() == "kp" else layer_name
        return f"tog{layer_name}"
    if behavior == "to" and args:
        return f"to{layer_name_by_index(layers, args[0])}"
    if behavior == "bt" and args:
        return f"BT{args[1]}" if args[0] == "BT_SEL" and len(args) > 1 else "BTclr"
    if behavior == "bl" and args:
        return {"BL_TOG": "BL", "BL_INC": "BL+", "BL_DEC": "BL-"}.get(args[0], "BL")
    if behavior == "rgb_ug" and args:
        return "RGB" if args[0] == "RGB_TOG" else args[0]
    if behavior == "stp" and args:
        return "Bat" if args[0] == "STP_BAT" else args[0]
    if behavior == "bootloader":
        return "Boot"
    if behavior == "studio_unlock":
        return "Studio"
    if behavior == "trans":
        return "trns"
    if behavior == "none":
        return "·"
    if behavior in BEHAVIOR_ALIASES:
        return BEHAVIOR_ALIASES[behavior]
    behavior_def = behaviors.get(behavior)
    if behavior_def and behavior_def.display_name:
        return compact_display_name(behavior_def.display_name)
    return behavior


def fit_label(label: str) -> str:
    """Pad or truncate a label to the fixed key-box width."""
    return label[:BOX_INNER_WIDTH].center(BOX_INNER_WIDTH)


def blank_key_box_line() -> str:
    """Return horizontal space equal to one rendered key box."""
    return " " * (BOX_INNER_WIDTH + 2)


def render_key_box(label: str, *, height_rows: int = 1) -> tuple[str, ...]:
    """Render one key box with a label row and optional blank interior rows."""
    if height_rows < 1:
        raise ValueError("key box height must be at least 1 row")
    border = "+" + "-" * BOX_INNER_WIDTH + "+"
    return (
        border,
        f"│{fit_label(label)}│",
        *(f"│{fit_label('')}│" for _ in range(height_rows - 1)),
        border,
    )


def render_key_row(labels: list[str]) -> tuple[str, str, str]:
    """Render one physical row as top, label, and bottom ASCII lines."""
    top = " ".join("+" + "-" * BOX_INNER_WIDTH + "+" for _ in labels)
    middle = " ".join(f"│{fit_label(label)}│" for label in labels)
    bottom = top
    return top, middle, bottom


def render_position_row(
    labels_by_position: dict[int, str],
    positions: tuple[int, ...],
) -> tuple[str, str, str]:
    """Render a row using physical position numbers."""
    return render_key_row([labels_by_position[position] for position in positions])


def render_bottom_thumb_row(
    labels_by_position: dict[int, str],
    positions: tuple[int, ...],
) -> tuple[str, ...]:
    """Render bottom thumb keys with 2u keys extending upward."""
    boxes = [
        render_key_box(
            labels_by_position[position],
            height_rows=2 if position in TALL_THUMB_POSITIONS else 1,
        )
        for position in positions
    ]
    row_height = max(len(box) for box in boxes)
    blank = blank_key_box_line()
    lines: list[str] = []
    for line_index in range(row_height):
        segments = [
            box[line_index - (row_height - len(box))]
            if line_index >= row_height - len(box)
            else blank
            for box in boxes
        ]
        lines.append(" ".join(segments))
    return tuple(lines)


def render_ascii(
    layer: LayerDef,
    behaviors: dict[str, BehaviorDef],
    layers: list[LayerDef],
    *,
    numbers: bool = False,
) -> str:
    """Render the selected layer in an ergonomic split ASCII layout."""
    if numbers:
        labels_by_position = {position: str(position) for position in range(EXPECTED_KEY_COUNT)}
    else:
        labels_by_position = {
            position: label_behavior(binding, behaviors=behaviors, layers=layers)
            for position, binding in enumerate(layer.bindings)
        }
    rendered_main_rows: list[tuple[tuple[str, str, str], tuple[str, str, str]]] = []
    half_width = 0
    for row_index, (left_positions, right_positions) in enumerate(zip(KEYS_L, KEYS_R, strict=True)):
        left = render_position_row(labels_by_position, left_positions)
        right = render_position_row(labels_by_position, right_positions)
        rendered_main_rows.append((left, right))
        half_width = max(
            half_width,
            len(" " * MAIN_INDENTS_L[row_index] + left[0]),
            len(" " * MAIN_INDENTS_R[row_index] + right[0]),
        )

    lines = [
        f"Advantage 360 Pro keymap: {layer.display_name} ({layer.node_name})",
        "",
    ]
    for row_index, (left, right) in enumerate(rendered_main_rows):
        for line_index in range(3):
            left_line = " " * MAIN_INDENTS_L[row_index] + left[line_index]
            right_line = " " * MAIN_INDENTS_R[row_index] + right[line_index]
            lines.append(left_line.ljust(half_width) + HALF_GAP + right_line)
    lines.append("")

    for row_index, (left_positions, right_positions) in enumerate(
        zip(THUMBS_L, THUMBS_R, strict=True)
    ):
        if row_index == len(THUMBS_L) - 1:
            left = render_bottom_thumb_row(labels_by_position, left_positions)
            right = render_bottom_thumb_row(labels_by_position, right_positions)
        else:
            left = render_position_row(labels_by_position, left_positions)
            right = render_position_row(labels_by_position, right_positions)
        for line_index in range(len(left)):
            left_line = left[line_index].rjust(half_width)
            right_line = right[line_index]
            lines.append(left_line + HALF_GAP + right_line)
    return "\n".join(lines)


def load_keymap(path: Path) -> tuple[list[LayerDef], dict[str, BehaviorDef]]:
    """Load and parse all renderable layers from a keymap file."""
    if not path.is_file():
        raise KeymapError(
            "keymap file does not exist",
            exit_code=ExitCode.USAGE_ERROR,
            context=str(path),
        )
    source = strip_comments(load_source_with_local_includes(path))
    behaviors = parse_behaviors(source)
    layers = parse_layers(source, behaviors)
    if not layers:
        raise KeymapError(
            "no renderable layers found",
            exit_code=ExitCode.DATA_ERROR,
            context=str(path),
        )
    return layers, behaviors


@APP.command()
def main(
    layer: Annotated[
        str,
        typer.Option(
            "--layer",
            "-l",
            help="Layer node name or display-name to render.",
        ),
    ] = "default_layer",
    file: Annotated[
        Path,
        typer.Option(
            "--file",
            "-f",
            help="Path to the ZMK .keymap file.",
        ),
    ] = DEFAULT_KEYMAP,
    numbers: Annotated[
        bool,
        typer.Option(
            "--numbers",
            "-n",
            help="Render physical position numbers instead of bindings.",
        ),
    ] = False,
) -> None:
    """Render an Advantage 360 Pro ZMK keymap layer as ASCII art."""
    try:
        keymap_file = file.expanduser()
        layers, behaviors = load_keymap(keymap_file)
        selected_layer = resolve_layer(layers, layer)
        typer.echo(render_ascii(selected_layer, behaviors, layers, numbers=numbers))
    except KeymapError as exc:
        message = f"error: {exc}"
        if exc.context:
            message = f"{message} ({exc.context})"
        typer.echo(message, err=True)
        raise typer.Exit(int(exc.exit_code)) from exc
    except OSError as exc:
        typer.echo(f"error: filesystem failure ({exc})", err=True)
        raise typer.Exit(int(ExitCode.RUNTIME_ERROR)) from exc


if __name__ == "__main__":
    try:
        APP()
    except KeyboardInterrupt:
        typer.echo("error: interrupted", err=True)
        sys.exit(int(ExitCode.RUNTIME_ERROR))
