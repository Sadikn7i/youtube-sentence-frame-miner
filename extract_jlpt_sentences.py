"""
JLPT Video → Clean Anki CSV Extractor
======================================
Extracts Japanese sentences + 4 answer choices from JLPT quiz video.
Output: anki_cards.csv (importable directly into Anki)

Format per card:
  Front: Japanese sentence (with underlined kanji as the quiz target)
  Back: 1 answer1  2 answer2  3 answer3  4 answer4  ✅ correct answer
"""

import os
import re
import subprocess
from PIL import Image
import pytesseract

# ── CONFIG ────────────────────────────────────────────────────────────────────
VIDEO_URL   = "https://www.youtube.com/watch?v=oBTmsQdulCE"
VIDEO_FILE  = "jlpt_video.f136.mp4"
OUTPUT_DIR  = "jlpt_frames"
RESULT_TXT  = "sentences_clean.txt"
ANKI_CSV    = "anki_cards.csv"
FRAME_RATE  = 20  # 1 frame every 16 seconds
LANGUAGE    = "jpn+eng"
# ─────────────────────────────────────────────────────────────────────────────

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
FFMPEG = r"C:\Users\dirir\Downloads\ffmpeg\ffmpeg-8.1.1-essentials_build\bin\ffmpeg.exe"

def extract_frames():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    existing = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".png")]
    if existing:
        print(f"Frames already extracted ({len(existing)} found). Skipping.")
        return
    print(f"Extracting 1 frame every {FRAME_RATE} seconds...")
    subprocess.check_call([
        FFMPEG, "-i", VIDEO_FILE,
        "-vf", f"fps=1/{FRAME_RATE}",
        f"{OUTPUT_DIR}/frame_%05d.png",
        "-hide_banner", "-loglevel", "error"
    ])
    print("Frame extraction complete.")

def is_japanese(text):
    """Check if text contains actual Japanese characters."""
    return bool(re.search(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]', text))

def extract_sentence(lines):
    """Find the main Japanese sentence (longest Japanese line, not options)."""
    candidates = []
    for line in lines:
        line = line.strip()
        # Skip lines that look like answer options (start with number)
        if re.match(r'^[1-4１-４][\s　]', line):
            continue
        # Skip short noise lines
        if len(line) < 5:
            continue
        if is_japanese(line):
            candidates.append(line)
    # Return the longest candidate (most likely the main sentence)
    if candidates:
        return max(candidates, key=len)
    return None

def extract_options(lines):
    """Extract the 4 reading options."""
    options = {}
    for line in lines:
        line = line.strip()
        # Match patterns like "1 てんどう" or "１ てんどう"
        m = re.match(r'^([1-4１-４])[\s　]+([ぁ-ん]+)', line)
        if m:
            num = str(m.group(1)).translate(str.maketrans('１２３４', '1234'))
            options[num] = m.group(2)
    return options

def extract_correct(lines):
    """Try to find boxed/correct answer — often shown as [3] or 【3】."""
    for line in lines:
        m = re.search(r'[\[【\(]([1-4])[\]】\)]', line)
        if m:
            return m.group(1)
    return "?"

def ocr_and_parse():
    frames = sorted(f for f in os.listdir(OUTPUT_DIR) if f.endswith(".png"))
    print(f"Running OCR on {len(frames)} frames...")

    cards = []
    last_sentence = ""

    for i, fname in enumerate(frames):
        path = os.path.join(OUTPUT_DIR, fname)
        img = Image.open(path)
        text = pytesseract.image_to_string(img, lang=LANGUAGE)
        lines = text.splitlines()

        sentence = extract_sentence(lines)
        if not sentence or sentence == last_sentence:
            continue

        options = extract_options(lines)
        if len(options) < 2:
            continue  # skip frames without answer options

        correct = extract_correct(lines)
        last_sentence = sentence

        cards.append({
            "sentence": sentence,
            "options": options,
            "correct": correct
        })

        opt_str = "  ".join([f"{k} {v}" for k, v in sorted(options.items())])
        print(f"  [{len(cards):>4}] {sentence[:50]}...")

        if i % 20 == 0:
            print(f"  Progress: {i}/{len(frames)} frames...")

    return cards

def save_results(cards):
    # Save readable text file
    with open(RESULT_TXT, "w", encoding="utf-8") as f:
        for i, c in enumerate(cards, 1):
            opts = "  ".join([f"{k} {v}" for k, v in sorted(c["options"].items())])
            f.write(f"--- {i} ---\n")
            f.write(f"{c['sentence']}\n")
            f.write(f"{opts}\n")
            f.write(f"✅ Answer: {c['correct']}\n\n")

    # Save Anki CSV (Front, Back)
    with open(ANKI_CSV, "w", encoding="utf-8") as f:
        for c in cards:
            opts = "  ".join([f"{k} {v}" for k, v in sorted(c["options"].items())])
            front = c["sentence"]
            back = f"{opts}<br>✅ {c['correct']}"
            # Escape quotes for CSV
            front = front.replace('"', '""')
            back = back.replace('"', '""')
            f.write(f'"{front}","{back}"\n')

    print(f"\n✅ {len(cards)} cards saved to {RESULT_TXT} and {ANKI_CSV}")

def main():
    extract_frames()
    cards = ocr_and_parse()
    save_results(cards)

if __name__ == "__main__":
    main()