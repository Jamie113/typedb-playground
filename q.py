#!/usr/bin/env python3
"""Run a TypeQL query against the local middle-earth database.

Usage:
  python3 q.py 'match $c isa character, has name $n; fetch { "name": $n };'
  python3 q.py --schema 'define entity orc, sub character;'
  python3 q.py --write  'insert $x isa hobbit, has name "Bilbo", has age 111;'
  echo 'match ...;' | python3 q.py        # read query from stdin

Default transaction type is read. --write / --schema switch it.
"""
import json, sys, urllib.request

BASE = "http://localhost:8000"

def signin():
    req = urllib.request.Request(
        f"{BASE}/v1/signin",
        data=json.dumps({"username": "admin", "password": "password"}).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["token"]

def main():
    args = sys.argv[1:]
    tx = "read"
    if args and args[0] == "--write":
        tx, args = "write", args[1:]
    elif args and args[0] == "--schema":
        tx, args = "schema", args[1:]
    query = " ".join(args) if args else sys.stdin.read()
    if not query.strip():
        print(__doc__); sys.exit(1)
    req = urllib.request.Request(
        f"{BASE}/v1/query",
        data=json.dumps({"databaseName": "middle-earth",
                         "transactionType": tx, "query": query}).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {signin()}"})
    try:
        with urllib.request.urlopen(req) as r:
            print(json.dumps(json.load(r), indent=2))
    except urllib.error.HTTPError as e:
        print(e.read().decode()); sys.exit(1)

if __name__ == "__main__":
    main()
