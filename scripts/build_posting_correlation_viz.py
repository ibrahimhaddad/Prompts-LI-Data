"""Parse Shares.csv + Connections.csv, correlate monthly posting frequency
against new connections, and render an interactive D3 dual-panel chart as
output/posting_correlation_viz.html.

Run from anywhere:  python scripts/build_posting_correlation_viz.py
"""
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_stats import pearson, spearman, ols, residuals_vs_time, diffs

REPO = Path(__file__).resolve().parent.parent
SHARES_CSV = REPO / "Shares.csv"
CONNECTIONS_CSV = REPO / "Connections.csv"
TEMPLATE = Path(__file__).resolve().parent / "templates" / "posting_correlation.template.html"
D3_JS = Path(__file__).resolve().parent / "vendor" / "d3.v7.min.js"
OUTPUT = REPO / "output" / "posting_correlation_viz.html"

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}


def parse_posts(path):
    raw_line_count = sum(1 for _ in open(path, encoding="utf-8-sig"))
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"Shares.csv: {raw_line_count} raw lines, {len(rows)} real post rows (proper CSV parse).")

    posts, bad = [], []
    for i, r in enumerate(rows):
        raw_date = (r.get("Date") or "").strip()
        dt = None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(raw_date, fmt)
                break
            except ValueError:
                continue
        if dt is None:
            bad.append((i, raw_date))
        else:
            posts.append(dt)

    print(f"Posts successfully dated: {len(posts)}  |  unparseable: {len(bad)}")
    for i, raw_date in bad:
        print(f"  BAD POST ROW {i}: Date={raw_date!r}")
    if posts:
        print(f"Post date range: {min(posts)} to {max(posts)}")
    return posts


def parse_connections(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        lines = f.readlines()
    header_idx = next(i for i, line in enumerate(lines) if line.startswith("First Name,Last Name"))
    print(f"\nConnections.csv: skipped {header_idx} preamble row(s).")
    rows = list(csv.DictReader("".join(lines[header_idx:]).splitlines()))
    print(f"Parsed {len(rows)} connection rows.")

    conns, bad = [], []
    for i, r in enumerate(rows):
        raw = (r.get("Connected On") or "").strip()
        dt = None
        try:
            day_s, mon_s, year_s = raw.split()
            dt = datetime(int(year_s), MONTHS[mon_s], int(day_s))
        except Exception:
            dt = None
        if dt is None:
            bad.append((i, raw))
        else:
            conns.append(dt)

    print(f"Connections successfully dated: {len(conns)}  |  unparseable: {len(bad)}")
    for i, raw in bad:
        print(f"  BAD CONN ROW {i}: 'Connected On'={raw!r}")
    if conns:
        print(f"Connection date range: {min(conns)} to {max(conns)}")
    return conns


def month_range(start, end):
    y, m = start
    out = []
    while (y, m) <= end:
        out.append((y, m))
        m += 1
        if m == 13:
            m, y = 1, y + 1
    return out


def analyze(posts, conns):
    first_post_month = (min(posts).year, min(posts).month)
    latest_month = max((max(posts).year, max(posts).month),
                        (max(conns).year, max(conns).month))
    months = month_range(first_post_month, latest_month)
    print(f"\nWindow: {months[0]} through {months[-1]} -> {len(months)} months")

    posts_by_month = defaultdict(int)
    for p in posts:
        posts_by_month[(p.year, p.month)] += 1
    conns_by_month = defaultdict(int)
    for c in conns:
        conns_by_month[(c.year, c.month)] += 1

    post_series = [posts_by_month.get(m, 0) for m in months]
    conn_series = [conns_by_month.get(m, 0) for m in months]
    conns_before_window = sum(1 for c in conns if (c.year, c.month) < first_post_month)

    print(f"Connections excluded (dated before window start): {conns_before_window}")

    r_raw, p_raw = pearson(post_series, conn_series)
    r_spear, p_spear = spearman(post_series, conn_series)
    r_detrend, p_detrend = pearson(residuals_vs_time(post_series), residuals_vs_time(conn_series))
    d_posts, d_conns = diffs(post_series), diffs(conn_series)
    r_diff, p_diff = pearson(d_posts, d_conns)
    slope, intercept = ols(post_series, conn_series)

    print("\n=== Correlation coefficients ===")
    print(f"Pearson r (raw levels):     r={r_raw:.4f}  p={p_raw:.4g}  n={len(months)}")
    print(f"Spearman rho (rank):        rho={r_spear:.4f}  p={p_spear:.4g}")
    print(f"Pearson r (detrended):      r={r_detrend:.4f}  p={p_detrend:.4g}")
    print(f"Pearson r (month-over-month diffs): r={r_diff:.4f}  p={p_diff:.4g}  n={len(d_posts)}")
    print(f"OLS fit (conn ~ posts): slope={slope:.4f}  intercept={intercept:.4f}")

    return {
        "months": [f"{y:04d}-{m:02d}" for y, m in months],
        "post_series": post_series,
        "conn_series": conn_series,
        "totals": {
            "posts_all": len(posts), "posts_in_window": sum(post_series),
            "conns_all": len(conns), "conns_in_window": sum(conn_series),
            "conns_before_window": conns_before_window,
        },
        "correlations": {
            "pearson_raw": {"r": r_raw, "p": p_raw, "n": len(months)},
            "spearman": {"rho": r_spear, "p": p_spear, "n": len(months)},
            "pearson_detrended": {"r": r_detrend, "p": p_detrend, "n": len(months)},
            "pearson_diff": {"r": r_diff, "p": p_diff, "n": len(d_posts)},
        },
        "ols": {"slope": slope, "intercept": intercept},
    }


def render(data):
    template = TEMPLATE.read_text(encoding="utf-8")
    d3js = D3_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
    data_json = json.dumps(data, ensure_ascii=False).replace("</script", "<\\/script")
    html = template.replace("/*__D3_JS__*/", d3js).replace("/*__DATA_JSON__*/", data_json)
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"\nWrote {OUTPUT}")


def main():
    if not SHARES_CSV.exists():
        raise SystemExit(f"Missing {SHARES_CSV} — put your LinkedIn Shares.csv export at the repo root.")
    if not CONNECTIONS_CSV.exists():
        raise SystemExit(f"Missing {CONNECTIONS_CSV} — put your LinkedIn Connections.csv export at the repo root.")
    posts = parse_posts(SHARES_CSV)
    conns = parse_connections(CONNECTIONS_CSV)
    data = analyze(posts, conns)
    render(data)


if __name__ == "__main__":
    main()
