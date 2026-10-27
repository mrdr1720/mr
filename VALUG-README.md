# VALUG weekly updater

## One-time setup (Mac)

1. Clone your blog repository if you do not already have it:
   `git clone https://github.com/mrdr1720/mr.git`
2. In Terminal, enter the repository folder:
   `cd mr`
3. Install the command:
   `python3 -m pip install -e .`

You can now run the updater from the repository folder:

```bash
valug 654.10 --date 2026-10-30
```

The command validates the date, adds the observation to `_data/valug.csv`, recalculates every signal, updates `_data/valug_signals.json`, creates a dated Jekyll post, commits the changes, and pushes to GitHub. GitHub Pages then rebuilds the site.

Useful options:

- Preview without changing files: `valug 654.10 --date 2026-10-30 --dry-run`
- Commit locally without pushing: `valug 654.10 --date 2026-10-30 --no-push`

The command refuses duplicate dates and dates older than the latest observation. For a historical correction, edit `_data/valug.csv` directly, then rerun the calculation workflow; the derived JSON is rebuilt whenever a new weekly close is added.

## Model assumptions

- One active state at a time: BUY or SELL.
- Initial state is assumed BUY on 2025-10-31, with reference high 642.50.
- BUY flips to SELL at a weekly close at or below 96% of the highest close since BUY.
- SELL flips to BUY at a weekly close at or above 104% of the lowest close since SELL.
- Only supplied weekly observations are evaluated. Holiday-shortened weeks retain their supplied dates.

Dashboard: `/valug/`.
