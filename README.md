# reeln-plugin-streamn-scoreboard

A [reeln-cli](https://github.com/StreamnDad/reeln-cli) plugin that bridges game initialization to the [streamn-scoreboard](https://github.com/StreamnDad/streamn-scoreboard) OBS plugin.

When `reeln game init` runs, this plugin automatically writes initial game state to the scoreboard's 17 text output files — setting team names, clock time, scores, shots, fouls, period, sport, and clearing penalties.

## Install

```bash
reeln plugin install streamn-scoreboard
```

Or for development:

```bash
git clone https://github.com/StreamnDad/reeln-plugin-streamn-scoreboard
cd reeln-plugin-streamn-scoreboard
make dev-install
```

## Configuration

Add the scoreboard plugin settings to your reeln-cli config:

```json
{
  "plugins": {
    "settings": {
      "streamn-scoreboard": {
        "output_directory": "/path/to/scoreboard/output"
      }
    }
  }
}
```

### Options

| Key | Required | Description |
|---|---|---|
| `output_directory` | Yes | Path to the scoreboard text file output directory |

### Output Files

| File | Content at game init |
|---|---|
| `clock.txt` | Formatted period length (e.g., `20:00`) |
| `period.txt` | `1` |
| `home_name.txt` | Home team name |
| `away_name.txt` | Away team name |
| `home_score.txt` | `0` |
| `away_score.txt` | `0` |
| `home_shots.txt` | `0` |
| `away_shots.txt` | `0` |
| `home_fouls.txt` | `0` |
| `away_fouls.txt` | `0` |
| `home_fouls2.txt` | `0` |
| `away_fouls2.txt` | `0` |
| `home_penalty_numbers.txt` | *(empty)* |
| `home_penalty_times.txt` | *(empty)* |
| `away_penalty_numbers.txt` | *(empty)* |
| `away_penalty_times.txt` | *(empty)* |
| `sport.txt` | Sport name (e.g., `hockey`) |

## Usage

Once installed and configured, the plugin activates automatically. Run:

```bash
reeln game init Eagles Hawks --sport hockey --level bantam
```

The plugin writes initial scoreboard state to the configured output directory. The OBS scoreboard's 100ms write loop takes over once the game is running.

### Clock Resolution

The clock value is resolved with the following priority:

1. `game_info.period_length` — set via `--period-length` CLI flag or interactive prompt
2. `home_profile.period_length` — from the team profile when `--level` is used
3. Sport-based default — fallback from the table below

### Supported Sports

| Sport | Default Clock | Notes |
|---|---|---|
| hockey | `20:00` | 20 min periods, count down |
| basketball | `12:00` | 12 min quarters |
| soccer | `45:00` | 45 min halves |
| football | `30:00` | 30 min halves |
| lacrosse | `12:00` | 12 min quarters |
| rugby | `40:00` | 40 min halves |
| baseball | `0:00` | No clock |
| generic | `0:00` | No default duration |

## Development

```bash
make dev-install    # editable install with dev deps
make test           # pytest with 100% coverage
make lint           # ruff check
make format         # ruff format
make check          # lint + type check + test
```

## License

AGPL-3.0
