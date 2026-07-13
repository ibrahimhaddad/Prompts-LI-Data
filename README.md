# Prompts LI Data

This repo contains 2 prompts to analyze your connections.csv and shares.csv exports from your LinkedIn Data. It connects directly to my LinkedIn post on this topic:

Have fun!

PS: Link to the LinkedIn post: https://www.linkedin.com/feed/update/urn:li:activity:7478093033599614976/

## Two ways to use this

**1. Hand the prompt to an AI assistant** (e.g. Claude) — give it `connections.md` and/or `posting.md` along with your exported CSVs, and let it do the parsing, analysis, and chart-building live. This costs tokens/usage on whatever assistant you use, but it's the most flexible option — you can ask follow-up questions, request different cuts of the data, or tweak the visualization on the spot.

**2. Run the provided scripts directly** — the exact same analysis, already implemented in `scripts/`, runs locally with plain Python and no AI calls at all. No tokens spent, fully deterministic, and just as fast. Use this if you just want the two HTML reports and don't need the back-and-forth.

Both paths produce the same two outputs: a company-cluster network graph and a posts-vs-connections correlation chart.

## Option 2: running the scripts locally

1. Export `Connections.csv` and `Shares.csv` from LinkedIn ([Settings & Privacy → Data privacy → Get a copy of your data](https://www.linkedin.com/psettings/member-data)) and drop them in the repo root, next to this README.
2. Requires Python 3.9+ — no extra packages to install (stdlib only, D3 is vendored under `scripts/vendor/`).
3. From the repo root, run either or both:

   ```
   python scripts/build_network_viz.py
   python scripts/build_posting_correlation_viz.py
   ```

Each script prints its parsing/clustering/correlation report to the console and writes a self-contained interactive HTML page to `output/`:

- `output/network_viz.html` — connections clustered by employer, as a force-directed D3 graph.
- `output/posting_correlation_viz.html` — monthly posts vs. new connections, with an OLS fit and four correlation coefficients (Pearson, Spearman, detrended, month-over-month).

Open either file directly in a browser. Re-run a script any time you re-export fresher CSVs — it just overwrites its `output/` file.

`Connections.csv`, `Shares.csv`, and `output/` are gitignored, since they contain your personal connection data.
