# typedb-playground

A throwaway world for learning **TypeDB 3.x** and **TypeQL** by poking at it.
The domain is a made-up **adventurers' guild** — warriors, mages, rogues,
monsters, quests. Small enough to hold in your head, rich enough to show the
things TypeDB does that SQL and Neo4j can't.

> Targets TypeDB 3.x (the Rust rewrite, Dec 2024+). The 2.x examples you'll
> find around the web use older syntax — make sure anything you copy says 3.x.

## What this playground is meant to teach

| File | Idea it shows off |
|------|-------------------|
| `schema.tql`  | Type hierarchy: `warrior`/`mage`/`rogue` **are** `adventurer`. Relations as real objects. |
| `data.tql`    | Inserting entities, then `match ... insert` to wire up relations. |
| `queries.tql` | Polymorphic queries, N-ary relations, nested `fetch`, negation, and a `fun` (function/reasoning). |

The three "aha"s to chase while you play:

1. **Polymorphism** — query 1 in `queries.tql` asks for `adventurer` and gets
   all three subtypes back. No `UNION`, no `type` column.
2. **N-ary relations** — a single `quest` object links several hunters, a
   monster, and a location at once (query 3). That's one pattern, not three
   join tables.
3. **Functions / reasoning** — query 6 derives "guildmates" that were never
   stored as a fact.

## Run it

### 1. Start a server (Docker)

```bash
docker volume create typedb-data
docker run --name typedb \
  -v typedb-data:/var/lib/typedb/data \
  -p 1729:1729 -p 8000:8000 \
  typedb/typedb:latest
```

### 2. Connect

Easiest: download **TypeDB Studio** (the GUI) and connect to `localhost:1729`.
Create a database (e.g. `guild`). Then, in order:

1. Open `schema.tql` → **schema** write transaction → run → **commit**.
2. Open `data.tql` → **data** write transaction → run → **commit**.
3. Open `queries.tql` → **read** transaction → run blocks one at a time.

(Query 6 defines a function, so run its `define` block in a **schema**
transaction and commit before calling it.)

Prefer the terminal? The `typedb console` CLI ships in the same Docker image
and runs the same `.tql` files.

## Stuff to try once it works (this is where the learning is)

- Add a `cleric` subtype of `adventurer` with a new `faith` attribute, reload
  the schema, and re-run query 1 — watch clerics appear with zero query changes.
- Make `party` own a `name`, give the parties names, and fetch quests *by party*.
- Write a function `veterans()` returning every adventurer with `level >= 12`.
- Add a `rivalry` relation and a query that finds adventurers who are both
  guildmates **and** rivals.
- Break something on purpose (wrong role name, missing `@key`) to see how the
  type checker complains — the error messages teach the model.

## Reference

- TypeDB Academy (do this alongside): https://typedb.com/docs/academy/
- TypeQL reference: https://typedb.com/docs/typeql/
- Get started: https://typedb.com/docs/home/get-started/

Made up data, made up monsters. Nothing here is real — that's the point.
