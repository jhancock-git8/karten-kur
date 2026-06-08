# karten-kur
Karten-Kur is a lightweight Python utility for cleaning and normalizing AlgoApp decks. It scans deck files and individual cards, detects common formatting problems, and applies safe, configurable fixes so decks are consistent and ready to study or export.

Key features
- Auto-detects and repairs malformed or corrupted card content (broken markup, unfinished tags, stray escape characters).  
- Normalizes formatting: trims extraneous whitespace, collapses repeated blank lines, enforces consistent line endings and paragraph spacing.  
- Standardizes card structure: ensures front/back fields follow a predictable layout, promotes consistent separators, and can reorder or rename fields.  
- Sanitizes text: removes invisible/control characters, fixes common Unicode issues (smart quotes, non-breaking spaces), and normalizes Unicode normalization form.  
- Configurable rules: enable/disable individual fixes, set custom regex-based transformations, and preview changes before applying.  
- Batch-safe operations: dry-run mode, automatic backups, and reversible change logs for safe bulk edits.  
- CLI-friendly: installable entry point (karten-kur), supports file/glob input, recursive folder processing, and verbose/quiet modes.  
- Extensible: plugin hooks or rule files to add deck-specific cleanup steps.

Intended uses
- Clean up decks imported from varied sources (exports, scraped content, OCR results) that contain inconsistent formatting.  
- Prepare decks for export, printing, or syncing with other apps by enforcing predictable card layouts.  
- Automate repetitive cleanup tasks across many decks while keeping a safe audit trail.

Implementation notes
- Package name: karten_kur; CLI: karten-kur.  
- Recommend using Unicode-normalization (NFC), Python’s regex module for flexible pattern handling, and unit tests for transformation rules.  
- Provide clear defaults that cover common cases but allow per-project configuration files (TOML/JSON/YAML).

LLM back-fill helper
- A new script at `python/fill_back_cards.py` can fill empty or too-short `Back` fields in an AlgoApp deck using an LLM.
- Defaults: input `input/kk2.xml`, output folder `output`, maximum 30 cards.
- Uses `ANTHROPIC_API_KEY` for Claude/Haiku or `OPENAI_API_KEY` for OpenAI.
- Output file is written as `output/<input_stem>_YYYYMMDD_HHMM.xml`.
- The script now treats Back fields with up to 2 words as needing fill by default.

Example:

    python python/fill_back_cards.py --input "input/kk2.xml" --output-dir "output" --max-fill 30 --max-back-words 2 --provider anthropic --model claude-haiku-4.5


Karten-Kur focuses on reliability and safety: it favors non-destructive defaults, offers previews and backups, and logs every change so you can trust automated repairs without losing original data.
