#!/usr/bin/env python3
"""Fill missing AlgoApp deck back-field content using an LLM API.

This script reads an AlgoApp deck XML file, finds cards whose Back field is empty,
and sends the Front field to a language model prompt that returns a back-of-card
response appropriate for AlgoApp flashcards.

Supported providers: anthropic (Claude/Haiku) and openai.

Environment variables:
- ANTHROPIC_API_KEY for Claude/Haiku
- OPENAI_API_KEY for OpenAI
"""

import argparse
import html
import json
import os
import re
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_PROVIDER = "anthropic"
DEFAULT_MODEL = "claude-haiku-4.5"
DEFAULT_MAX_FILL = 30
DEFAULT_MAX_BACK_WORDS = 2
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_API_TIMEOUT = 60

PROMPT_TEMPLATE = """Bitte beachte diese Anweisungen für diesen Chat.

Jede Nachricht, die ich sende, enthält ein deutsches Wort oder eine deutsche Redewendung.

Deine Antwort dient als Grundlage für eine Karteikarte.

Erster Abschnitt (Englisch): Kurze Liste passender englischer Übersetzungen oder Entsprechungen.

Zweiter Abschnitt (Deutsch): Mehrere natürliche Beispielsätze, jeweils als vollständige Sätze. Jeder Satz muss das gegebene Wort oder die Redewendung enthalten. Schreibe die Sätze direkt hintereinander, getrennt durch zwei Leerzeichen. Verwende keine Anführungszeichen und füge keine Einleitung wie „Beispiele:“ hinzu.

Dritter Abschnitt (Deutsch): Knappe Wörterbuch-Erklärung der Bedeutung und typischen Verwendung. Konzentriere dich auf Nuancen, Register (umgangssprachlich, formell usw.) und mögliche Stolpersteine für Deutschlernende. Maximal 60 Wörter.

Formatierungsregeln:

* Genau drei Absätze ausgeben.
* Keine Überschriften oder Beschriftungen hinzufügen.
* Keine Aufzählungszeichen oder Nummerierung verwenden.
* Keine Anführungszeichen verwenden.
* Keine einleitenden Wörter wie „Beispiele:“ oder ähnliche Labels verwenden.
* Keine horizontalen Linien oder Trennzeichen verwenden.

Human: {word}

Assistant:"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fill empty back-of-card fields in an AlgoApp deck XML file using an LLM."
    )
    parser.add_argument("--input", default=r"c:\_repos\karten-kur\input\kk2.xml",
                        help="Input AlgoApp deck XML file")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR,
                        help="Output directory for the filled deck file")
    parser.add_argument("--max-fill", type=int, default=DEFAULT_MAX_FILL,
                        help="Maximum number of cards to fill")
    parser.add_argument("--max-back-words", type=int, default=DEFAULT_MAX_BACK_WORDS,
                        help="Treat cards with Back text shorter than or equal to this word count as needing fill")
    parser.add_argument("--provider", choices=("anthropic", "openai"),
                        default=DEFAULT_PROVIDER,
                        help="LLM API provider to use")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help="LLM model name to use")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show which cards would be filled without calling the API")
    parser.add_argument("--verbose", action="store_true",
                        help="Print progress information")
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
    return tree, root, cards_parent, cards


def get_text(field):
    if field is None or field.text is None:
        return ""
    return field.text.strip()


def normalize_back_text(text):
    unescaped = html.unescape(text or "")
    no_tags = re.sub(r"<[^>]+>", " ", unescaped)
    cleaned = re.sub(r"[^\wäöüÄÖÜß'-]+", " ", no_tags)
    return cleaned.strip()


def back_needs_fill(card, max_back_words):
    back = card.find("rich-text[@name='Back']")
    if back is None:
        return True

    back_text = get_text(back)
    if not back_text:
        return True

    normalized = normalize_back_text(back_text)
    word_count = len(re.findall(r"\b[\wäöüÄÖÜß'-]+\b", normalized))
    return word_count <= max_back_words


def build_prompt(word):
    return PROMPT_TEMPLATE.format(word=word)


def call_anthropic(prompt, model):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY is not set")

    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "max_tokens_to_sample": 900,
        "temperature": 0.2,
        "top_k": 1,
        "top_p": 1,
    }).encode("utf-8")

    request = Request(
        "https://api.anthropic.com/v1/complete",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Api-Key": api_key,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=DEFAULT_API_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload.get("completion", "").strip()
    except HTTPError as exc:
        raise RuntimeError(f"Anthropic API error {exc.code}: {exc.read().decode('utf-8')}" )
    except URLError as exc:
        raise RuntimeError(f"Anthropic API request failed: {exc}")


def call_openai(prompt, model):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set")

    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 900,
    }).encode("utf-8")

    request = Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=DEFAULT_API_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload["choices"][0]["message"]["content"].strip()
    except HTTPError as exc:
        raise RuntimeError(f"OpenAI API error {exc.code}: {exc.read().decode('utf-8')}" )
    except URLError as exc:
        raise RuntimeError(f"OpenAI API request failed: {exc}")


def call_llm(prompt, provider, model):
    if provider == "anthropic":
        return call_anthropic(prompt, model)
    return call_openai(prompt, model)


def ensure_back_field(card):
    back = card.find("rich-text[@name='Back']")
    if back is None:
        fields = card.findall("rich-text")
        insert_index = len(fields)
        back = ET.Element("rich-text", {"name": "Back"})
        card.insert(insert_index, back)
    return back


def write_deck(tree, output_dir, source_file):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    source_stem = Path(source_file).stem
    target_name = f"{source_stem}_{timestamp}.xml"
    target_path = output_path / target_name
    tree.write(str(target_path), encoding="utf-8", xml_declaration=True)
    return target_path


def main():
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    tree, _, _, cards = load_deck(input_path)
    cards_to_fill = [card for card in cards if back_needs_fill(card, args.max_back_words)]
    fill_count = min(len(cards_to_fill), args.max_fill)

    if args.verbose:
        print(f"Found {len(cards_to_fill)} cards with short or empty Back fields")
        print(f"Will fill up to {fill_count} cards")

    if fill_count == 0:
        print("No empty Back fields found or max-fill is zero. No changes made.")
        return

    if args.dry_run:
        print("Dry run mode: the following card fronts would be filled:")
        for index, card in enumerate(cards_to_fill[:fill_count], start=1):
            front = get_text(card.find("rich-text[@name='Front']"))
            print(f"{index}. {front}")
        return

    for index, card in enumerate(cards_to_fill[:fill_count], start=1):
        front_text = get_text(card.find("rich-text[@name='Front']"))
        if args.verbose:
            print(f"[{index}/{fill_count}] Filling card front: {front_text}")

        prompt = build_prompt(front_text)
        completion = call_llm(prompt, args.provider, args.model)
        if not completion:
            raise RuntimeError(f"Empty response from LLM for word: {front_text}")

        back_field = ensure_back_field(card)
        back_field.text = completion

    target_path = write_deck(tree, args.output_dir, input_path)
    print(f"Updated deck written to: {target_path}")
    print(f"Filled {fill_count} back-of-card fields.")


if __name__ == "__main__":
    main()
