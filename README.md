# typedb-playground

A throwaway **Middle-earth** for learning **TypeDB 3.x** and **TypeQL** by
poking at it. The domain is Lord of the Rings — hobbits, elves, dwarves, men,
wizards, the Fellowship, the Quest. Recognisable data so you can tell at a
glance *what* a query returned and *why*.

> Targets TypeDB 3.x (the Rust rewrite, Dec 2024+). The 2.x examples you'll
> find around the web use older syntax — make sure anything you copy says 3.x.

## Why Lord of the Rings is a good teacher here

Tolkien's world lines up with TypeDB's three signature ideas almost perfectly:

| TypeDB idea | In Middle-earth |
|-------------|-----------------|
| **Type hierarchy / polymorphism** | hobbit, elf, dwarf, man, wizard all **are** `character`. Query `character`, get all five races back — no `UNION`, no race column. |
| **N-ary relations** (a relation is a real object, not an edge or join table) | The **Fellowship** is one object with nine members. The **Quest** links a bearer + the Ring + a destination in a single pattern. |
| **Functions / reasoning** | "Aragorn's countrymen" (anyone sworn to the same realm) is *derived*, never stored. |

## Files

| File | What it covers |
|------|----------------|
| `schema.tql`  | The races as subtypes of `character`; relations (fellowship, friendship, allegiance, quest, battle). |
| `data.tql`    | Inserting characters/realms, then `match ... insert` to wire up the Fellowship, friendships, allegiances, the Quest. |
| `queries.tql` | Polymorphic queries, N-ary relations, nested `fetch`, negation, and a `fun` (function/reasoning). |
| `schema-ext.tql` | **Expansion schema:** genealogy (`parentship`), geography (`road`), a `war` relation *over battles*, multi-valued/`datetime` attributes, a `rivalry` relation, and two recursive functions. |
| `data-ext.tql`   | **Expansion data:** the line of Kings, Elrond's kin, a road network (with a cycle), epithets, battle dates, the War of the Ring, rivalries. |
| `queries-ext.tql`| **Advanced queries:** recursion, transitive closure, aggregation, multi-valued attributes, nested relations, and rivalry-on-a-shared-battlefield. |
| `load.py`     | Loads a `.tql` file over the HTTP API, splitting it into its query blocks: `python3 load.py schema.tql schema`, `python3 load.py data.tql write`. |
| `q.py`        | Runs a single query: `python3 q.py '<typeql>'` (read), or `--write` / `--schema` to change data/schema. |

### The expansion layer (stretch goals)

The `*-ext.tql` files push past the basics into TypeDB's distinctive
capabilities. Load them *after* the base files:

```bash
python3 load.py schema-ext.tql schema
python3 load.py data-ext.tql   write
python3 load.py queries-ext.tql read    # smoke-test all 8 advanced queries
```

| Capability | Where to see it | Why it's hard elsewhere |
|------------|-----------------|-------------------------|
| **Recursion** | `ancestors($c)` walks a whole lineage from one self-calling function | no `WITH RECURSIVE` ceremony |
| **Transitive closure** | `reachable($r)` follows the road graph any number of hops, terminating despite cycles | graph reachability in SQL is painful |
| **Aggregation** | `reduce count(...), mean(...) groupby $t` — stats per race | — |
| **Multi-valued attrs** | a character owns several `epithet`s; `[ $c.epithet ]` collects them | no array column needed |
| **Relations over relations** | `war` relates `battle`s, which are themselves relations | a join table can't hold a row whose members are rows |
| **Rivalry on a shared field** | query 8 stacks a relation, an n-ary relation, and matches the same battle twice | — |
| **Paths: route + distance** | `path_within($r, $hops)` returns destination, a route string, and total distance in one recursive function; `reduce min` gives the shortest | weighted pathfinding with the route, not just reachability |

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

**GUI:** download **TypeDB Studio**, connect to `localhost:1729`, create a
database (e.g. `middle-earth`), then in order:

1. Open `schema.tql` → **schema** write transaction → run → **commit**.
2. Open `data.tql` → **data** write transaction → run → **commit**.
3. Open `queries.tql` → **read** transaction → run blocks one at a time.

(Query 7 defines a function, so run its `define` block in a **schema**
transaction and commit before calling it.)

**Terminal:** the server image does *not* bundle `typedb console`, so the
included Python helpers drive the HTTP API on port `8000` instead (stdlib
only, no deps). After the server is up:

```bash
curl -s -X POST localhost:8000/v1/databases/middle-earth \
  -H "Authorization: Bearer $(curl -s -X POST localhost:8000/v1/signin \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"password"}' | sed 's/.*"token":"//;s/".*//')"
python3 load.py schema.tql schema     # define the schema
python3 load.py data.tql   write      # insert + wire up the world
python3 q.py 'match $c isa character, has name $n; fetch { "name": $n };'
```

> The helpers use TypeDB's default `admin`/`password` credentials — fine for a
> local throwaway, not for anything exposed.

> **3.11.x syntax note:** calling a function uses `let $x in fun(...)`, and a
> bound relation variable links its players with `$r links (role: $p)`. The
> queries in `queries.tql` already use these forms.

## Stuff to try once it works (this is where the learning is)

- Add an `orc` subtype of `character` (e.g. Lurtz, Gothmog), reload the
  schema, and re-run query 1 — watch orcs appear with zero query changes.
- The Fellowship is one big relation. Write a query for everyone who fought at
  **Helm's Deep** (the `battle` relation) but was **not** in the Fellowship.
- Give `wizard` an `order` attribute and find every wizard "of the white".
- Write a function `kin()` returning every character of the same race as a
  given character (hint: `$x isa $t; $other isa $t;`).
- Add `Sauron`, a `Mordor` allegiance, and a `rivalry` relation, then find
  characters who are enemies of someone they share a battlefield with.
- Break something on purpose (wrong role name, missing `@key`) to see how the
  type checker complains — the error messages teach the model.

## Reference

- TypeDB Academy (do this alongside): https://typedb.com/docs/academy/
- TypeQL reference: https://typedb.com/docs/typeql/
- Get started: https://typedb.com/docs/home/get-started/

Built on a beloved made-up world so the *data* is never the hard part —
only the database is.
