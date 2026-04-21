# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.6.0] - 2026-04-14

### Added

- Write `period_length.txt` with period duration in seconds — enables OBS plugin to sync custom period lengths from reeln team profiles
- Populate `context.shared["home_score"]` and `context.shared["away_score"]` on `ON_GAME_FINISH` — downstream plugins can now access final game score
- Output now matches all 23 files written by OBS scoreboard plugin v0.7.0

### Fixed

- Sport duration defaults now match OBS plugin — hockey 20→15 min, basketball 12→8 min; prevents clock mismatch on game init when no custom period length is set

## [0.5.4] - 2026-03-26

### Fixed

- Remove `reeln` from package metadata entirely — PyPI rejects direct git URL dependencies even in optional extras
- Disable PyPI attestations in release workflow to fix upload failures
- Install `reeln` separately in CI/release workflows

### Changed

- Version bump for PyPI re-publish (v0.5.0–v0.5.3 uploads failed)

## [0.5.0] - 2026-03-26

### Added

- Write `home_faceoffs.txt`, `away_faceoffs.txt` faceoff win counters (hockey, lacrosse)
- Write `period_labels.txt` with sport-specific defaults (e.g. hockey: 1, 2, 3, OT, OT2, OT3, OT4) or custom labels from `GameInfo.period_labels`
- `get_default_period_labels()` helper for generating sport-appropriate period label sets
- Output now matches all 22 files written by OBS scoreboard plugin v0.5.0

## [0.4.0] - 2026-03-14

### Added

- `ON_GAME_FINISH` hook handler — copies `timestamps.txt` from the OBS scoreboard output directory to `chapters.txt` in the game directory for downstream reeln-cli use (YouTube chapter descriptions, ffmpeg chapter injection)
- Populates `context.shared["game_events"]` with parsed timestamp entries for inter-plugin communication (Google plugin YouTube chapter insertion)
- Clear stale `timestamps.txt` during `ON_GAME_INIT` to prevent previous game session data from leaking into a new game's finish

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
