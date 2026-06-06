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

Karten-Kur focuses on reliability and safety: it favors non-destructive defaults, offers previews and backups, and logs every change so you can trust automated repairs without losing original data.
