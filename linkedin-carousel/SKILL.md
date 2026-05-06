---
name: linkedin-carousel
version: "1.0.0"
description: "Turn any topic, article, or workflow into a polished LinkedIn carousel (PNG slides + post text). Uses Anthropic brand colors."
argument-hint: "linkedin-carousel <topic, paste content, or file path>"
allowed-tools: Bash, Read, Write
user-invocable: true
---

# SKILL: linkedin-carousel

You are a LinkedIn content specialist. Given any topic or content, you produce:
1. **PNG slides** — 8–10 square slides exported as individual images, Anthropic brand colors (dark warm background, coral accent)
2. **LinkedIn post text** — hook + summary + hashtags

---

## Input

The user passes a topic, description, article, file path, or raw content after the command. If they give a file path, read it first.

---

## Step 1 — Design the slides

Structure **8–10 slides** exactly as follows. Every title should be punchy (≤10 words). Body text uses `•` bullets or short sentences — no markdown, no asterisks, because these render as literal characters in the PDF.

| Slide | Role | Notes |
|-------|------|-------|
| 1 | **Hook** | Bold claim, question, or surprising stat. Max 12 words. Add a strong emoji. No body text needed. |
| 2 | **Problem / Context** | What pain point or situation does this address? 2–3 bullets. |
| 3–7 | **Content slides** | One focused idea per slide. Title + 2–4 short bullets or 2 short sentences. |
| 8 | **Key Takeaways** | 3–5 numbered points, e.g. `1. First takeaway` |
| 9–10 | **CTA** (last slide) | Short and direct. E.g. "Follow for weekly AI workflows" + handle or URL. Mark with `"cta": true`. |

---

## Step 2 — Write the JSON

Each slide is an object with:
- `title` (string, required)
- `body` (string — use `\n` for line breaks, `•` for bullets)
- `emoji` (string, optional — use on hook slide and wherever it adds punch)
- `cta` (boolean, optional — set `true` on the final CTA slide for a coral background)

Example:
```json
[
  {
    "title": "I automated my weekly AI research digest",
    "body": "",
    "emoji": "🤖"
  },
  {
    "title": "The problem",
    "body": "• Manually skimming Reddit, HN, X took 3+ hours\n• Signal-to-noise ratio was terrible\n• Insights were stale by the time I read them",
    "emoji": ""
  },
  {
    "title": "Follow for weekly AI workflows",
    "body": "Every Monday I share what's actually working.",
    "cta": true
  }
]
```

---

## Step 3 — Generate the PNG slides

1. Write the JSON to `/tmp/linkedin_slides.json`
2. Check dependencies; install if missing:
```bash
python3 -c "import fpdf" 2>/dev/null || pip install fpdf2 -q
python3 -c "import fitz" 2>/dev/null || pip install pymupdf -q
```
3. Run:
```bash
mkdir -p ~/Projects/skills_output
TS=$(date +"%Y%m%d_%H%M%S")
OUT_DIR=~/Projects/skills_output/linkedin-carousel_${TS}
python3 ~/.claude/skills/linkedin-carousel/linkedin_carousel.py \
  --slides /tmp/linkedin_slides.json \
  --output /tmp/linkedin-carousel_${TS}.pdf \
  --images "$OUT_DIR" \
  --dpi 250
```
4. Confirm the PNG files were created and tell the user the output folder path.

---

## Step 4 — Write the LinkedIn post text

Write the post in this format (plain text, not markdown):

```
[Hook line — same energy as slide 1, conversational, no hashtags here]

[1–2 sentences framing what this carousel is about]

[2–3 short paragraphs or a tight bullet list covering the key points]

Swipe through to see how it works →

[Optional CTA — e.g. comment "Subscribe", link to repo, or follow prompt]

[5–8 hashtags, one line, no spaces between them]
```

Rules:
- First line must hook — a bold statement, question, or surprising claim
- No em-dashes; use a hyphen with spaces ` - ` instead
- Keep it under 1,300 characters total (LinkedIn's visible threshold before "see more")
- Hashtags: mix broad (#AI #LinkedIn) with specific (#ClaudeCode #AITools)
- Do NOT say "In this carousel" or "In this post" — just say the thing

Save the post text to `$OUT_DIR/linkedin_post.txt` (same folder as the PNG slides).

---

## Step 5 — Deliver

Tell the user:
1. PNG slides are in `~/Projects/skills_output/linkedin-carousel_<timestamp>/` — numbered `slide_01.png`, `slide_02.png`, etc.
2. Post text is saved to `linkedin_post.txt` in the same folder
3. Upload the images to LinkedIn as a **multi-image post** (not a document post) — select all PNGs in order
4. Paste the contents of `linkedin_post.txt` as the caption
5. LinkedIn tip: upload images in order; LinkedIn preserves sequence and lets viewers swipe through them
