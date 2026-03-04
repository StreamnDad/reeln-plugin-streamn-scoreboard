# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.3.0] - 2026-03-03

### Added

- Write `sport.txt` file matching OBS scoreboard `write_all_files()` output
- Write `home_fouls.txt`, `away_fouls.txt` foul counters (basketball fouls, soccer YC, football flags)
- Write `home_fouls2.txt`, `away_fouls2.txt` second foul counters (soccer red cards)
- Rugby sport support (40-minute halves)
- Output now matches all 17 files written by OBS scoreboard plugin

## [0.2.0] - 2026-03-03

### Added

- Use `period_length` from team profiles to set scoreboard clock when available
- Falls back to sport-based clock mapping when no team profile is provided

## [0.1.0]

### Added

- Initial plugin implementation
- `ScoreboardPlugin` subscribes to `ON_GAME_INIT` hook
- `ScoreboardWriter` writes 12 text files matching OBS scoreboard format
- Sport-to-clock mapping for hockey, basketball, soccer, football, lacrosse, baseball, generic
- Configurable output directory and filename overrides
