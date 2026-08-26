# TODO

## Next Tasks

- [x] Extracted PDF chapters caching system
  - [x] Responsabilità esclusiva della cache:
  - [x] Calcolare l'hash SHA-256 del PDF;
  - [x] Determinare il path della cache;
  - [x] Salvare list[Chapter];
  - [x] Caricare list[Chapter];
  - [x] Distinguere cache mancante da cache corrotta.
- [x] ChaptersNotFoundError and similar errors must retry a few times when rised
- [x] Add a function for removing the "#" from the text in the chapter selection dropdown
- [x] Error handling without app crash
  - [x] Only the final errors that would block the app should be displayed in the app window for a few seconds as a popup. The retriable errors which will be retried must not display the popup.
- [x] New view for the playback
- [x] Add a bottom row with play button for starting audio (copy the one from the UI Slider)
- [x] Add buttons to go Forward and Backword one line in the bottom row
- [x] Add printing lines on the new window
- [x] Add cursor/selection following current lines
- [x] Packaging with Pyinstaller
- [x] Create README

## Bugs

- [x] Fix UI bugs when loading a new PDF file
- [x] Fix regeneration logic when changing mode or level
  - [x] Prevent audio from being marked as ready immediately
  - [x] Ensure the generation process starts again correctly
  - [x] Fix generate button state after starting regeneration

## Refactoring / Code Quality

- [x] Implement TypeError handling in `extractor.py`
- [x] Fix and complete docstrings in `tts.py`

## Features

- [x] Implement caching system for:
  - [x] Extracted PDF chapters
  - [x] Generated audio files
- [x] Implement MP3 playback
- [x] Add live SRT reading tracker
- [x] Packaging with Pyinstaller

## Documentation

- [x] Create `README.md`

# Project Completion Criteria

- [x] All known bugs fixed
- [x] Core pipeline completed:
  - [x] PDF extraction
  - [x] Chapter processing
  - [x] Script generation
  - [x] TTS generation
  - [x] Audio playback
  - [x] SRT Tracking
- [x] Caching implemented
- [x] Packaging with Pyinstaller
- [x] Documentation/README completed

# Tips Prof

Model view controller
