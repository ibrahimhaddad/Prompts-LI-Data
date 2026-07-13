"""Parse Connections.csv, cluster by normalized company, and render an
interactive D3 force-directed network as output/network_viz.html.

Run from anywhere:  python scripts/build_network_viz.py
"""
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONNECTIONS_CSV = REPO / "Connections.csv"
TEMPLATE = Path(__file__).resolve().parent / "templates" / "network_viz.template.html"
D3_JS = Path(__file__).resolve().parent / "vendor" / "d3.v7.min.js"
OUTPUT = REPO / "output" / "network_viz.html"

TOP_N = 20
LEAF_CAP_THRESHOLD = 1500
LEAF_CAP_PER_HUB = 40

SUFFIX_RE = re.compile(
    r"[,\s]+(Inc\.?|L\.?L\.?C\.?|Ltd\.?|Limited|Corp\.?|Corporation|GmbH|AG|S\.?A\.?|PLC|Plc|"
    r"Co\.?|Company|A/S|ApS|Oyj?|B\.?V\.?|N\.?V\.?|Pty\.?\s*Ltd\.?|Pte\.?\s*Ltd\.?|SARL|S\.?R\.?L\.?|SE|AB)\.?$",
    re.IGNORECASE,
)


def strip_suffix(s):
    m = SUFFIX_RE.search(s)
    if m:
        return s[: m.start()].strip().rstrip(",.").strip()
    return s


def parse_connections(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        lines = f.readlines()
    header_idx = next(i for i, line in enumerate(lines) if line.startswith("First Name,Last Name"))
    print(f"Skipped {header_idx} preamble row(s) before the header.")
    reader = csv.DictReader("".join(lines[header_idx:]).splitlines())
    rows = list(reader)
    print(f"Parsed {len(rows)} connection rows.")
    return rows


def cluster(rows):
    total = len(rows)
    raw_counter = Counter()
    for r in rows:
        c = (r.get("Company") or "").strip()
        raw_counter[c or "Independent / Unknown"] += 1

    casefold_groups = defaultdict(list)
    for raw, cnt in raw_counter.items():
        casefold_groups[raw.casefold()].append((raw, cnt))

    casefold_repr = {}
    case_merges = []
    for key, variants in casefold_groups.items():
        variants.sort(key=lambda x: (-x[1], x[0]))
        rep = variants[0][0]
        casefold_repr[key] = (rep, sum(c for _, c in variants))
        if len(variants) > 1 and key != "independent / unknown":
            case_merges.append((rep, variants))

    stripped_key_of = {}
    for key, (rep, _) in casefold_repr.items():
        stripped_key_of[key] = key if key == "independent / unknown" else strip_suffix(rep).casefold()

    suffix_groups = defaultdict(list)
    for key, skey in stripped_key_of.items():
        suffix_groups[skey].append(key)

    final_clusters = {}
    cluster_members = {}
    suffix_merges = []
    for skey, ckeys in suffix_groups.items():
        members = [casefold_repr[k] for k in ckeys]
        members.sort(key=lambda x: (-x[1], len(x[0]), x[0]))
        label = members[0][0]
        final_clusters[label] = sum(c for _, c in members)
        cluster_members[label] = members
        if len(members) > 1 and skey != "independent / unknown":
            suffix_merges.append((label, members))

    raw_to_label = {}
    for label, members in cluster_members.items():
        for rep, _ in members:
            for raw, cnt in raw_counter.items():
                if raw.casefold() == rep.casefold():
                    raw_to_label[raw] = label

    print(f"\n{len(raw_counter)} distinct raw company strings -> {len(final_clusters)} clusters after normalization.")
    print("\nCase-normalization merges (same company, different casing):")
    if not case_merges:
        print("  none found")
    for rep, variants in sorted(case_merges, key=lambda x: -sum(c for _, c in x[1])):
        print(f"  -> {rep}: " + ", ".join(f"'{v}'({c})" for v, c in variants))

    print("\nSuffix-stripping merges (legal-suffix variants of the same employer):")
    if not suffix_merges:
        print("  none found")
    for label, members in sorted(suffix_merges, key=lambda x: -sum(c for _, c in x[1])):
        print(f"  -> {label}: " + ", ".join(f"'{m}'({c})" for m, c in members))

    return total, final_clusters, raw_to_label


def build_people(rows, raw_to_label):
    people = []
    for r in rows:
        c = (r.get("Company") or "").strip() or "Independent / Unknown"
        people.append({
            "first": r.get("First Name", ""),
            "last": r.get("Last Name", ""),
            "position": (r.get("Position") or "").strip(),
            "cluster": raw_to_label[c],
        })
    return people


def build_viz_data(total, final_clusters, people):
    ranked = sorted(final_clusters.items(), key=lambda x: (-x[1], x[0]))
    top20 = ranked[:TOP_N]
    top20_labels = {label for label, _ in top20}

    by_cluster = defaultdict(list)
    other_count = 0
    for p in people:
        if p["cluster"] in top20_labels:
            by_cluster[p["cluster"]].append(p)
        else:
            other_count += 1

    top20_sum = sum(c for _, c in top20)
    cap_applied = top20_sum > LEAF_CAP_THRESHOLD

    nodes = [{"id": "__me__", "type": "center", "name": "Me", "count": total}]
    links = []
    for rank_i, (label, cnt) in enumerate(top20, 1):
        hub_id = f"hub::{label}"
        nodes.append({"id": hub_id, "type": "hub", "name": label, "count": cnt, "rank": rank_i})
        links.append({"source": "__me__", "target": hub_id})
        members = by_cluster[label]
        shown = members[:LEAF_CAP_PER_HUB] if cap_applied else members
        for p in shown:
            full_name = f"{p['first']} {p['last']}".strip()
            leaf_id = f"leaf::{label}::{full_name}::{len(nodes)}"
            nodes.append({"id": leaf_id, "type": "leaf", "name": full_name,
                          "position": p["position"], "hub": label})
            links.append({"source": hub_id, "target": leaf_id})

    nodes.append({"id": "hub::Other", "type": "other", "name": "Other", "count": other_count, "rank": TOP_N + 1})
    links.append({"source": "__me__", "target": "hub::Other"})

    return {
        "total": total,
        "distinctCompanies": len(ranked),
        "top20Sum": top20_sum,
        "otherCount": other_count,
        "largest": {"label": ranked[0][0], "count": ranked[0][1]},
        "capApplied": cap_applied,
        "top20": [{"rank": i + 1, "label": l, "count": c, "pct": round(c / total * 100, 2)}
                  for i, (l, c) in enumerate(top20)],
        "nodes": nodes,
        "links": links,
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
    if not CONNECTIONS_CSV.exists():
        raise SystemExit(f"Missing {CONNECTIONS_CSV} — put your LinkedIn Connections.csv export at the repo root.")
    rows = parse_connections(CONNECTIONS_CSV)
    total, final_clusters, raw_to_label = cluster(rows)
    people = build_people(rows, raw_to_label)
    data = build_viz_data(total, final_clusters, people)

    print(f"\nTop {TOP_N} clusters:")
    for row in data["top20"]:
        print(f"  {row['rank']:2d}. {row['label']:40s} {row['count']:4d}  {row['pct']:5.2f}%")
    print(f"\nOutside top {TOP_N} ('Other'): {data['otherCount']}")
    if data["capApplied"]:
        print(f"Top-20 population ({data['top20Sum']}) exceeds {LEAF_CAP_THRESHOLD} — capped at {LEAF_CAP_PER_HUB} leaves/hub.")

    render(data)


if __name__ == "__main__":
    main()
