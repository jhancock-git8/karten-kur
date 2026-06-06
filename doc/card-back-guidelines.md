# Card Back Integration Ideas for Karten-Kur

This document describes how Karten-Kur can help add, improve, and regularize card backs for AlgoApp deck exports.

## Goal

Provide a consistent and useful card-back structure for German vocabulary cards with three paragraphs:

1. English meanings
2. Sample sentences in German
3. Discussion of usage and connotations in German

This format improves readability, review speed, and study value.

## Suggested card-back schema

Each card back should follow a simple normalized structure, ideally using clean HTML or a standardized plaintext format.

### Recommended paragraph structure

- Paragraph 1: short English meaning(s)
- Paragraph 2: one or two German sample sentences
- Paragraph 3: usage notes, register, connotation, and any important nuance in German

Example:

```html
<p>to take off, to remove</p>
<p>Er zog sich die Jacke aus, weil es im Raum zu warm war.</p>
<p>„ausziehen" ist ein alltägliches Verb; im Kontext von Kleidung ist es neutral und sehr gebräuchlich.</p>
```

## How Karten-Kur can integrate this pattern

### 1. Detect and classify existing back content

- Identify whether a card back already contains a three-paragraph structure.
- Detect common formatting styles:
  - plain text definitions
  - HTML fragments with `<p>`, `<em>`, `<span>`
  - embedded cloze markers or unusual spans
- Flag cards that deviate from the schema for review.

### 2. Normalize rich text content

- Convert rich-text HTML fragments into a normalized form:
  - preserve `<p>` and `<em>` for emphasis
  - remove unsupported or risky tags (`<div>`, `<table>`, inline scripts, complex nested layout)
  - remove redundant `style` attributes unless needed for emphasis
- Convert `&nbsp;`, `&lt;`, `&gt;` and other escaped entities back to normalized HTML text when appropriate.

### 3. Enforce the three-paragraph layout

- For cards with a single paragraph or no structure, provide a guided transformation:
  - split a lengthy back field into definition / example / usage sections
  - preserve all original content, but reorder or rephrase into the target format
- For cards with more than three paragraphs, classify paragraph roles and suggest a condensed version.

### 4. Add helpful metadata and validation

- Use the deck cleanup workflow to validate card backs before export:
  - ensure there is at least one English meaning phrase
  - ensure there is at least one German sentence in the second paragraph
  - ensure the third paragraph contains usage/connotation language and not just more example sentences
- Report cards missing any of the three sections.

## Practical integration ideas

### A. Deck import pipeline

When importing AlgoApp XML:

- parse the `Back` and `Front` rich-text fields
- normalize card back HTML
- detect cloze/experimental formatting and either convert it or flag it
- optionally split the deck into smaller chunks for safe export or study

### B. Regularization rules

Implement rules such as:

- `card_back_minimum_paragraphs: 3`
- `card_back_preferred_tags: [p, em, strong, br]`
- `card_back_disallow_tags: [div, table, script, iframe, input]`
- `card_back_trim_spaces: true`
- `card_back_fix_entities: true`

These rules make the back content consistent and reduce crashes caused by unsupported formatting.

### C. Optional auto-augmentation

If a card is missing a good back structure, Karten-Kur could offer a helper mode to generate or complete it:

- extract the English meaning from the existing back or front
- create one or two clean German example sentences from the card term
- add a short usage note based on common patterns

This should be treated as a suggestion, not an automatic overwrite.

## Why this is useful

- Stable export: AlgoApp and other flashcard apps often fail on unexpected HTML or cloze markup.
- Better study quality: consistent backs help you read and review cards faster.
- Easier maintenance: structured backs are simpler to clean, edit, and extend.

## Practical recommendation for current workflow

- Keep the `Front` field as the German term.
- Keep the `Back` field as the single rich-text card back.
- Use a normalized three-paragraph structure for the back.
- Use Karten-Kur to detect and fix formatting issues before re-import or export.

## Example of a regularized back

```html
<p>to print; to publish</p>
<p>Die Zeitung wird jeden Morgen gedruckt und im Bahnhof verkauft.</p>
<p>„drucken" ist ein sehr häufiges Verb in Medien- und Bürokontexten; es passt sowohl für Papier als auch für digitale Veröffentlichungen.</p>
```

This layout keeps the back focused, readable, and compatible with most card apps.
