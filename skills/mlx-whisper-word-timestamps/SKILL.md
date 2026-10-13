---
name: mlx-whisper-word-timestamps
description: Transcribe a user-supplied MP3 with mlx-whisper and return one JSON object per spoken word with word-level start and end timestamps. Use when exact timestamped transcription JSON is requested.
---

# MLX Whisper Word Timestamps

Invoke this skill with one mandatory audio path:

`$mlx-whisper-word-timestamps /absolute/path/to/audio.mp3`

An optional full narration may follow the path as recognition context, but it never replaces transcription from the audio:

`$mlx-whisper-word-timestamps /absolute/path/to/audio.mp3 --narration "..."`

## Requirements

- Supported device: macOS on an Apple-silicon Mac (M1/M2/M3/M4 or newer) with the MLX runtime. This workflow is not intended for Windows, Linux, Intel Macs, iOS, or Android devices.
- Runtime: Python 3 in a virtual environment is recommended.
- Required package: `mlx-whisper` (which installs `mlx`, `mlx-metal`, and its transcription dependencies such as `numpy`, `numba`, `scipy`, and `tiktoken`). Install with `python3 -m pip install mlx-whisper` when it is not already available.
- Model: an MLX Whisper model, preferably already cached locally. If no local model is available, the selected `mlx-community` model must be downloaded once before it can be used offline.
- Input: an existing readable audio file; MP3 is the expected input format.

## Workflow

1. Require exactly one existing audio path. If it is missing, ask for it; do not infer a default file. Resolve relative paths before processing.
2. Use `mlx_whisper.transcribe` with `word_timestamps=True` and `language="en"`. Use the locally available MLX Whisper model; prefer a cached local model, and inspect the environment for the existing Python or virtual environment before installing anything.
3. Build the result from every returned word entry in segment order. Preserve contractions and every recognized word. Strip only leading and trailing punctuation from `word`; retain internal apostrophes and hyphens. Keep the model's word boundaries—do not merge, split, or deduplicate entries.
4. Emit a JSON array only. Each item must have exactly `word`, `start`, and `end`. Format both timestamps to three decimal places and preserve that formatting in the JSON output (for example, `0.000`, not `0`). Do not emit markdown fences, explanation, logs, or narration text.

The optional narration can help identify an obvious recognition mismatch, but timestamps and word inclusion must come from the audio transcription. If the model omits or inserts a word relative to the narration, return the audio-derived words rather than silently editing them.

## Completion criteria

The response is complete only when the entire audio has been processed and the final response contains valid JSON with one object for every returned word, punctuation-free word fields, and three-decimal start/end timestamps—nothing outside the JSON array.
