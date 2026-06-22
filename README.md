
A Python pipeline that extracts Japanese sentences from silent JLPT quiz videos and outputs clean Anki-ready flashcards.

## Overview

This tool automates the process of mining Japanese sentences from YouTube JLPT study videos that display kanji quiz slides. It downloads the video, extracts frames, runs OCR on each frame, filters out noise, and produces a clean CSV file importable into Anki.

## Requirements

### Software

- Python 3.8+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) with Japanese language pack
- [ffmpeg](https://www.gyan.dev/ffmpeg/builds/)

### Python Libraries

```
pip install yt-dlp pytesseract Pillow opencv-python
```

## Installation

1. Clone the repository

```
git clone https://github.com/yourusername/jlpt-extractor.git
cd jlpt-extractor
```

2. Install Python dependencies

```
pip install yt-dlp pytesseract Pillow opencv-python
```

3. Install Tesseract OCR and select Japanese during installation

4. Install ffmpeg and note the path to the bin folder

5. Update the paths at the top of `extract_jlpt_sentences.py`

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
FFMPEG = r"C:\path\to\ffmpeg\bin\ffmpeg.exe"
```

## Configuration

All settings are at the top of the script.

| Variable | Default | Description |
|---|---|---|
| VIDEO_URL | YouTube URL | Target video to process |
| VIDEO_FILE | jlpt_video.f136.mp4 | Downloaded video filename |
| OUTPUT_DIR | jlpt_frames_v2 | Folder to store extracted frames |
| FRAME_RATE | 5 | Extract one frame every N seconds |
| LANGUAGE | jpn | Tesseract OCR language |

## Usage

Update the `VIDEO_URL` variable in the script with your target video, then run:

```
python extract_jlpt_sentences.py
```

## Pipeline

1. yt-dlp downloads the YouTube video to disk
2. ffmpeg extracts one frame every N seconds
3. Each frame is preprocessed with grayscale conversion, contrast boost, and sharpening
4. Tesseract OCR reads the Japanese text from each frame
5. Noise and answer options are filtered out
6. Only the main Japanese sentence is kept per unique slide
7. Results are saved to two output files

## Output

| File | Description |
|---|---|
| sentences_clean.txt | Numbered list of all extracted sentences |
| anki_cards.csv | CSV file ready to import into Anki |

## Importing into Anki

1. Open Anki
2. File > Import
3. Select `anki_cards.csv`
4. Set the separator to Comma
5. Map the first field to Front
6. Import

## Limitations

- OCR accuracy depends on video resolution and font clarity
- Transition frames may produce garbled output which is filtered out automatically
- Videos without clear text slides are not supported
- Auto-generated YouTube captions are not used; all extraction is done via OCR

## Tech Stack

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - video downloading
- [ffmpeg](https://ffmpeg.org/) - frame extraction
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - optical character recognition
- [Pillow](https://python-pillow.org/) - image preprocessing
- [pytesseract](https://github.com/madmaze/pytesseract) - Python wrapper for Tesseract
