#!/usr/bin/env python3
"""Load .tql files into TypeDB 3.x over the HTTP API.

Splits a .tql file into its individual query blocks (a block starts at a
top-level `match`, or at a `define`/`insert` that isn't the insert-clause of
the current match block) and posts each one in its own auto-committing
transaction of the given type.
"""
import json, sys, urllib.request

BASE = "http://localhost:8000"

def signin():
    req = urllib.request.Request(
        f"{BASE}/v1/signin",
        data=json.dumps({"username": "admin", "password": "password"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(req))["token"]

def split_blocks(text):
    blocks, cur, seen_write = [], [], False
    def flush():
        nonlocal cur, seen_write
        if any(l.strip() for l in cur):
            blocks.append("\n".join(cur))
        cur, seen_write = [], False
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        head = s.split()[0] if not line[:1].isspace() else ""
        if head in ("match", "define"):
            flush(); cur.append(line); seen_write = head == "define"
        elif head == "insert":
            if seen_write:
                flush()
            cur.append(line); seen_write = True
        else:
            cur.append(line)
    flush()
    return blocks

def run(token, tx_type, query):
    req = urllib.request.Request(
        f"{BASE}/v1/query",
        data=json.dumps({"databaseName": "middle-earth",
                         "transactionType": tx_type, "query": query}).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            return True, r.read().decode()
    except urllib.error.HTTPError as e:
        return False, e.read().decode()

def main():
    path, tx_type = sys.argv[1], sys.argv[2]
    token = signin()
    blocks = split_blocks(open(path).read())
    print(f"== {path}  ({tx_type})  {len(blocks)} block(s) ==")
    for i, b in enumerate(blocks, 1):
        ok, body = run(token, tx_type, b)
        first = b.strip().splitlines()[0]
        tag = "OK " if ok else "ERR"
        print(f"[{tag}] block {i}: {first[:60]}")
        if not ok:
            print("       " + body[:400])
            sys.exit(1)
    print("done.")

if __name__ == "__main__":
    main()
