#!/usr/bin/env python3
"""Split an AlgoApp deck XML export and report atypical card formatting."""

import argparse
import html
import os
import re
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

SUSPICIOUS_PATTERNS = [
    re.compile(r"\{\{c\d+::", re.I),
    re.compile(r"\{\{[^}]+::", re.I),
    re.compile(r"\[\[.*?\]\]", re.I),
    re.compile(r"class=\"cloze\"", re.I),
    re.compile(r"data-cloze", re.I),
    re.compile(r"<span[^>]*(class|data)-", re.I),
    re.compile(r"<(?:(?:div|table|script|style|iframe|object|applet|input|textarea|select|button))\b", re.I),
    re.compile(r"\\r|\\n|\\t|&#13;", re.I),
]

ALLOWED_HTML_TAGS = re.compile(r"<\s*/?\s*(?:p|em|strong|span|br|b|i|u|ul|li|ol|sup|sub|small|blockquote|cite|span|a)[^>]*>", re.I)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Split an AlgoApp deck XML file into smaller deck files and scan for atypical formatting."
    )
    parser.add_argument("input", help="Input AlgoApp deck XML file")
    parser.add_argument("--output-dir", default="output", help="Output directory for split files")
    parser.add_argument("--cards-per-deck", type=int, default=1125, help="Maximum cards per split deck")
    parser.add_argument("--dry-run", action="store_true", help="Scan without writing split files")
    parser.add_argument("--verbose", action="store_true", help="Print more detail")
    return parser.parse_args()


def load_deck(path):
    tree = ET.parse(str(path))
    root = tree.getroot()
    if root.tag != "deck":
        raise ValueError(f"Expected <deck> root element, found <{root.tag}>")

    cards_parent = root.find("cards")
    if cards_parent is None:
        raise ValueError("Deck XML does not contain a <cards> element")

    cards = list(cards_parent.findall("card"))
    if not cards:
        raise ValueError("Deck XML contains no <card> entries")

    return tree, root, cards_parent, cards


def scan_card(card):
    notes = []
    for field in card.findall("rich-text"):
        field_name = field.get("name") or "unknown"
        text = field.text or ""
        unescaped = html.unescape(text)
        stripped = text.strip()

        if not stripped:
            notes.append(f"{field_name}: empty field")
            continue

        if any(pattern.search(text) for pattern in SUSPICIOUS_PATTERNS):
            notes.append(f"{field_name}: suspicious formatting or cloze marker")

        if re.search(r"(?i)(class=\"cloze\"|data-cloze|\{\{c\d+::|\[\[|\{\{[^}]+::)", unescaped):
            notes.append(f"{field_name}: cloze-like marker in unescaped text")

        if re.search(r"<span[^>]*style=|<span[^>]*class=|<br\s*/?>|<em>|<strong>|<b>|<i>|<u>", unescaped, re.I):
            notes.append(f"{field_name}: rich HTML formatting detected")

        if re.search(r"<[^>]+>", unescaped) and not ALLOWED_HTML_TAGS.search(unescaped):
            notes.append(f"{field_name}: unexpected HTML tags present")

        paragraph_count = len(re.findall(r"<\s*/?\s*p\b", unescaped, re.I))
        if paragraph_count > 2:
            notes.append(f"{field_name}: {paragraph_count} paragraph tags")

    return notes


def collect_suspicious_cards(cards):
    suspicious = []
    for index, card in enumerate(cards, start=1):
        notes = scan_card(card)
        if notes:
            front = card.find("rich-text[@name='Front']")
            back = card.find("rich-text[@name='Back']")
            suspicious.append({
                "index": index,
                "notes": notes,
                "front": front.text.strip() if front is not None and front.text else "",
                "back": back.text.strip() if back is not None and back.text else "",
            })
    return suspicious


def build_split_roots(root, cards, cards_per_deck):
    deck_name = root.get("name", "deck")
    template_root = deepcopy(root)
    template_cards = template_root.find("cards")
    for child in list(template_cards):
        template_cards.remove(child)

    chunks = [cards[i : i + cards_per_deck] for i in range(0, len(cards), cards_per_deck)]
    split_roots = []
    for index, chunk in enumerate(chunks, start=1):
        subroot = deepcopy(template_root)
        subroot.set("name", f"{deck_name} - part {index}")
        cards_element = subroot.find("cards")
        for card in chunk:
            cards_element.append(deepcopy(card))
        split_roots.append((index, subroot, len(chunk)))
    return split_roots


def write_split_files(split_roots, output_dir, source_file):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    generated = []
    source_stem = Path(source_file).stem

    for index, subroot, card_count in split_roots:
        out_name = f"{source_stem}-part{index}.xml"
        target_path = output_path / out_name
        tree = ET.ElementTree(subroot)
        tree.write(str(target_path), encoding="utf-8", xml_declaration=True)
        generated.append((target_path, card_count))
    return generated


def print_report(cards, suspicious, generated):
    print("Deck scan report")
    print("---------------")
    print(f"Total cards: {len(cards)}")
    print(f"Suspicious cards found: {len(suspicious)}")
    if suspicious:
        print("\nSuspicious cards:")
        for item in suspicious:
            print(f"  - card {item['index']}: {item['front'] or item['back']}")
            for note in item["notes"]:
                print(f"      * {note}")

    if generated:
        print("\nSplit output files:")
        for path, count in generated:
            print(f"  - {path} ({count} cards)")


def main():
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    tree, root, _, cards = load_deck(input_path)
    suspicious = collect_suspicious_cards(cards)
    split_roots = build_split_roots(root, cards, args.cards_per_deck)

    generated = []
    if not args.dry_run:
        generated = write_split_files(split_roots, args.output_dir, input_path)
    else:
        print(f"Dry run: would create {len(split_roots)} split deck files")
        for index, _, card_count in split_roots:
            print(f"  part {index}: {card_count} cards")

    print_report(cards, suspicious, generated)

    if args.verbose and suspicious:
        print("\nVerbose suspicious card details: unescaped snippets")
        for item in suspicious:
            print(f"--- card {item['index']} ---")
            print(f"Front: {item['front']}\nBack: {item['back']}\n")


if __name__ == "__main__":
    main()
