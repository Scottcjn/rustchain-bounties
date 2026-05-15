#!/usr/bin/env python3
"""
RustChain QR Wallet Address Generator
Generate QR codes for RTC wallet addresses with customizable colors and sizes.
"""

import qrcode
import argparse
import json
import os
from pathlib import Path

# RustChain address prefix
RTC_PREFIX = "rtc1"

# Default QR code settings
DEFAULT_SIZE = 10  # pixels per module
DEFAULT_BORDER = 4
DEFAULT_FILL_COLOR = "000000"
DEFAULT_BG_COLOR = "FFFFFF"


def validate_rtc_address(address: str) -> bool:
    """Validate a RustChain wallet address format."""
    if not address.startswith(RTC_PREFIX):
        return False
    if len(address) < 40 or len(address) > 64:
        return False
    return all(c.isalnum() for c in address[len(RTC_PREFIX):])


def generate_wallet_qr(
    address: str,
    output: str = "wallet_qr.png",
    fill_color: str = DEFAULT_FILL_COLOR,
    bg_color: str = DEFAULT_BG_COLOR,
    size: int = DEFAULT_SIZE,
    border: int = DEFAULT_BORDER,
    amount: float = None,
    label: str = None,
) -> str:
    """
    Generate a QR code for a RustChain wallet address.

    Args:
        address: RTC wallet address
        output: Output file path
        fill_color: QR code foreground color (hex, e.g. 'FF0000')
        bg_color: QR code background color (hex, e.g. 'FFFFFF')
        size: Pixel size per QR module
        border: Border size in modules
        amount: Optional amount to encode in URI
        label: Optional label for the address

    Returns:
        Path to generated QR code image
    """
    if not validate_rtc_address(address):
        raise ValueError(f"Invalid RTC address: {address}")

    # Build RTC URI
    uri = f"rustchain:{address}"
    params = []
    if amount is not None:
        params.append(f"amount={amount}")
    if label is not None:
        params.append(f"label={label}")
    if params:
        uri += "?" + "&".join(params)

    # Normalize colors
    if not fill_color.startswith("#"):
        fill_color = f"#{fill_color}"
    if not bg_color.startswith("#"):
        bg_color = f"#{bg_color}"

    qr = qrcode.QRCode(
        version=None,  # auto-detect
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=size,
        border=border,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=bg_color)
    img.save(output)
    return output


def batch_generate(config_path: str) -> list:
    """
    Batch generate QR codes from a JSON config file.

    Config format:
    [
        {
            "address": "rtc1...",
            "output": "wallet1_qr.png",
            "fill_color": "000000",
            "bg_color": "FFFFFF",
            "size": 10,
            "amount": 100.0,
            "label": "My Wallet"
        }
    ]
    """
    with open(config_path, "r") as f:
        configs = json.load(f)

    results = []
    for cfg in configs:
        output = generate_wallet_qr(
            address=cfg["address"],
            output=cfg.get("output", f"qr_{cfg['address'][:12]}.png"),
            fill_color=cfg.get("fill_color", DEFAULT_FILL_COLOR),
            bg_color=cfg.get("bg_color", DEFAULT_BG_COLOR),
            size=cfg.get("size", DEFAULT_SIZE),
            border=cfg.get("border", DEFAULT_BORDER),
            amount=cfg.get("amount"),
            label=cfg.get("label"),
        )
        results.append(output)
        print(f"✅ Generated: {output}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="RustChain QR Wallet Address Generator"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Single QR generation
    gen = subparsers.add_parser("generate", help="Generate QR code for a wallet address")
    gen.add_argument("address", help="RTC wallet address (rtc1...)")
    gen.add_argument("-o", "--output", default="wallet_qr.png", help="Output file path")
    gen.add_argument("-f", "--fill-color", default=DEFAULT_FILL_COLOR, help="QR foreground color (hex)")
    gen.add_argument("-b", "--bg-color", default=DEFAULT_BG_COLOR, help="QR background color (hex)")
    gen.add_argument("-s", "--size", type=int, default=DEFAULT_SIZE, help="Pixels per module")
    gen.add_argument("--border", type=int, default=DEFAULT_BORDER, help="Border size in modules")
    gen.add_argument("--amount", type=float, help="Amount to encode in URI")
    gen.add_argument("--label", help="Label for the address")

    # Batch generation
    batch = subparsers.add_parser("batch", help="Batch generate from JSON config")
    batch.add_argument("config", help="Path to JSON config file")

    # Validate address
    val = subparsers.add_parser("validate", help="Validate an RTC address")
    val.add_argument("address", help="RTC wallet address to validate")

    args = parser.parse_args()

    if args.command == "generate":
        output = generate_wallet_qr(
            address=args.address,
            output=args.output,
            fill_color=args.fill_color,
            bg_color=args.bg_color,
            size=args.size,
            border=args.border,
            amount=args.amount,
            label=args.label,
        )
        print(f"✅ QR code saved to: {output}")
    elif args.command == "batch":
        results = batch_generate(args.config)
        print(f"\n✅ Generated {len(results)} QR codes")
    elif args.command == "validate":
        if validate_rtc_address(args.address):
            print(f"✅ Valid RTC address: {args.address}")
        else:
            print(f"❌ Invalid RTC address: {args.address}")
            exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
