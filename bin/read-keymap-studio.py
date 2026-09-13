#!/usr/bin/env python3
"""Read the current keymap from an Advantage 360 Pro over ZMK Studio RPC."""

from __future__ import annotations

import argparse
import sys

import serial.tools.list_ports
import zmk_studio_api as zmk
from zmk_studio_cli.proto import core_pb2 as core
from zmk_studio_cli.proto import keymap_pb2 as keymap
from zmk_studio_cli.proto import studio_pb2 as studio

KINESIS_VID = 0x29EA
KINESIS_PID = 0x0362
EXPECTED_POSITIONS = 76


def find_keyboard_port() -> str | None:
    """Return the first Kinesis Advantage 360 Pro CDC/ACM serial port."""
    for port in serial.tools.list_ports.comports():
        if port.vid == KINESIS_VID and port.pid == KINESIS_PID:
            return str(port.device)
        if port.product and "Adv360" in port.product:
            return str(port.device)
        if port.manufacturer and "Kinesis" in port.manufacturer:
            return str(port.device)
    return None


def decode_device_info(raw: bytes) -> core.GetDeviceInfoResponse | None:
    """Decode raw device-info bytes from ZMK Studio RPC."""
    info = core.GetDeviceInfoResponse()
    try:
        info.ParseFromString(raw)
    except Exception:
        return None
    return info


def decode_keymap(raw: bytes) -> keymap.Keymap | None:
    """Decode raw keymap bytes from ZMK Studio RPC."""
    response = studio.Response()
    response.ParseFromString(raw)
    if response.WhichOneof("type") != "request_response":
        return None
    rr = response.request_response
    if rr.WhichOneof("subsystem") != "keymap":
        return None
    km_resp = rr.keymap
    if km_resp.WhichOneof("response") != "get_keymap":
        return None
    return km_resp.get_keymap


def format_behavior(behavior: zmk.Behavior) -> str:
    """Return a compact string for a typed ZMK behavior."""
    if isinstance(behavior, zmk.KeyPress):
        return f"kp({behavior})"
    if isinstance(behavior, zmk.NoBehavior):
        return "none"
    if isinstance(behavior, zmk.Transparent):
        return "trans"
    if isinstance(behavior, zmk.MomentaryLayer):
        return f"mo({behavior.layer})"
    if isinstance(behavior, zmk.ToggleLayer):
        return f"tg({behavior.layer})"
    if isinstance(behavior, zmk.ToLayer):
        return f"to({behavior.layer})"
    if isinstance(behavior, zmk.LayerTap):
        return f"lt({behavior.layer},{behavior.behavior})"
    if isinstance(behavior, zmk.ModTap):
        return f"mt({behavior.modifiers},{behavior.behavior})"
    if isinstance(behavior, zmk.KeyToggle):
        return f"kt({behavior})"
    if isinstance(behavior, zmk.KeyRepeat):
        return "repeat"
    if isinstance(behavior, zmk.StudioUnlock):
        return "studio_unlock"
    if isinstance(behavior, zmk.Bootloader):
        return "boot"
    if isinstance(behavior, zmk.Reset):
        return "reset"
    if isinstance(behavior, zmk.SoftOff):
        return "soft_off"
    if isinstance(behavior, zmk.OutputSelection):
        return f"out({behavior})"
    if isinstance(behavior, zmk.Bluetooth):
        return f"bt({behavior})"
    if isinstance(behavior, zmk.CapsWord):
        return "caps_word"
    if isinstance(behavior, zmk.StickyKey):
        return f"sk({behavior})"
    if isinstance(behavior, zmk.StickyLayer):
        return f"sl({behavior.layer})"
    if isinstance(behavior, zmk.Raw):
        return f"raw({behavior.behavior_id},{behavior.param1},{behavior.param2})"
    return str(behavior)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read the current keymap from an Advantage 360 Pro over ZMK Studio RPC."
    )
    parser.add_argument(
        "--port",
        "-p",
        help="Serial port path (skip auto-discovery)",
    )
    parser.add_argument(
        "--layer",
        "-l",
        type=int,
        help="Only read and print a single layer by index",
    )
    args = parser.parse_args(argv)

    port = args.port or find_keyboard_port()
    if not port:
        print(
            "error: no Kinesis Advantage 360 Pro serial port found",
            file=sys.stderr,
        )
        return 1

    print(f"Connecting to {port} ...")
    client = zmk.StudioClient.open_serial(port)

    lock = client.get_lock_state()
    print(f"Studio lock state: {lock}")

    dev_info = decode_device_info(client.get_device_info_bytes())
    if dev_info:
        print(f"Device: {dev_info.name}")

    if "locked" in str(lock).lower():
        print(
            "note: keymap is locked; press the studio_unlock key and rerun to read bindings."
        )
        return 0

    try:
        km = decode_keymap(client.get_keymap_bytes())
    except RuntimeError as exc:
        print(f"error: failed to read keymap: {exc}", file=sys.stderr)
        return 1
    if km is None:
        print("error: failed to decode keymap", file=sys.stderr)
        return 1

    layers = list(km.layers)
    if args.layer is not None:
        if args.layer < 0 or args.layer >= len(layers):
            print(f"error: layer index {args.layer} out of range (0-{len(layers)-1})", file=sys.stderr)
            return 1
        layers = [layers[args.layer]]

    for layer in layers:
        print(f"\nLayer {layer.id}: {layer.name}")
        positions = range(EXPECTED_POSITIONS)
        for position in positions:
            try:
                behavior = client.get_key_at(layer.id, position)
                label = format_behavior(behavior)
            except RuntimeError as exc:
                label = f"<error: {exc}>"
            print(f"  {position:2d}: {label}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
