#!/usr/bin/env python3
"""
Localization script: translate a RustChain documentation file into a target language
using the googletrans library (unofficial Google Translate API).
"""

import sys
import argparse
from pathlib import Path
from googletrans import Translator, LANGUAGES


def _normalize_language_code(lang_input: str) -> str:
    """
    Convert a language name or code to a valid googletrans language code.
    Returns the code or raises ValueError if not recognized.
    """
    lang = lang_input.strip().lower()
    if lang in LANGUAGES:
        return lang
    # Try matching by language name
    for code, name in LANGUAGES.items():
        if name.lower() == lang:
            return code
    raise ValueError(f"Language '{lang_input}' not recognized.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Translate a RustChain doc into a target language."
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Path to the source documentation file (UTF-8).",
    )
    parser.add_argument(
        "-l",
        "--lang",
        required=True,
        help="Target language code (e.g., 'es') or full name (e.g., 'Spanish').",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path. If omitted, prints to stdout.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run a built-in test translation and exit.",
    )
    args = parser.parse_args()

    if args.test:
        # Built‑in demo: translate a short sentence to several languages.
        translator = Translator()
        sample = "Welcome to RustChain documentation."
        print(f'Source: "{sample}"')
        for target_code, target_name in list(LANGUAGES.items())[:5]:  # show first 5
            try:
                translated = translator.translate(sample, dest=target_code)
                print(f"{target_name} ({target_code}): {translated.text}")
            except Exception as e:
                print(f"{target_name} ({target_code}): ERROR - {e}")
        return

    if not args.source.is_file():
        sys.exit(f"Error: source file '{args.source}' does not exist.")

    try:
        target_lang = _normalize_language_code(args.lang)
    except ValueError as err:
        sys.exit(str(err))

    text = args.source.read_text(encoding="utf-8")
    translator = Translator()

    try:
        translated = translator.translate(text, dest=target_lang)
    except Exception as e:
        sys.exit(f"Translation failed: {e}")

    output_text = translated.text
    if args.output:
        args.output.write_text(output_text, encoding="utf-8")
        print(f"Translation written to {args.output}")
    else:
        print(output_text)


if __name__ == "__main__":
    # When invoked without arguments, show a brief usage hint.
    if len(sys.argv) == 1:
        print(
            "Usage: python translate_doc.py <source_file> -l <target_language> [-o <output_file>]\n"
            "Example: python translate_doc.py README.md -l es -o README_es.md\n"
            "Use --test to see a quick demo."
        )
    else:
        main()