"""Robust loader for pilot CSVs written by appending rows with different column sets.

Pilot 1 wrote each worker's header from its first row (ion2020, Lmax 2: 99 columns). ionproj rows (Lmax 3) carry six extra
h3_* columns placed just before 'umax' (105 fields). The rows are positional and complete, so they are re-keyed here exactly:
a 105-field row maps to the header with the h3 block inserted before 'umax'. Any other field count is an error."""
import csv, io
import pandas as pd
H3 = ["h3_users", "h3_paths_mean", "h3_served", "h3_users_bad", "h3_deliv", "h3_bad"]


def load(path):
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    head = rows[0]
    long_head = head if "h3_users" in head else head[:head.index("umax")] + H3 + head[head.index("umax"):]
    short_head = [c for c in long_head if c not in H3]
    recs = []
    for r in rows[1:]:
        if len(r) == len(long_head): recs.append(dict(zip(long_head, r)))
        elif len(r) == len(short_head): recs.append(dict(zip(short_head, r)))
        else: raise ValueError(f"{path}: row with {len(r)} fields (expected {len(short_head)} or {len(long_head)})")
    buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=long_head); w.writeheader(); w.writerows(recs); buf.seek(0)
    return pd.read_csv(buf)                                  # same typing as a normal read_csv of a well-formed file
