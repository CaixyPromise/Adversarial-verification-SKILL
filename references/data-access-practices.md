# Data Access, Cache & Transaction Review

**When to read:** changed persistence, cache, database schema, queue or consistency-sensitive paths. Primarily Agent C (systems), with A validating business invariants and B comparing project conventions. Select relevant probes; not every query needs a performance investigation.

## Establish the real data path

Trace **request → service → transaction → SQL/ORM/cache → external effects**, and determine realistic cardinality, request rate, availability/consistency expectations and actual DB/cache versions. Missing workload evidence means no invented scaling claim.

## Queries, ORM and indexing

- **N+1:** inspect repeated queries inside loops and ORM lazy loading. On a nontrivial list or hot path, test/trace query count versus input size. Prefer bounded batch lookup, selective prefetch or justified joins; do not eager-load whole graphs or require optimization for insignificant tiny workloads.
- **Index fit:** compare `WHERE`, `JOIN`, `ORDER BY`, composite index prefixes, selectivity and pagination with existing indexes and real plans. Evaluate write amplification and maintenance. **"Column is filtered" alone is not evidence an index is needed**.
- **Query plans:** use DB-specific `EXPLAIN` / safe representative benchmarks when available; full scans may be correct for small tables. Do not run invasive `EXPLAIN ANALYZE` or data-changing probes on production.
- **Data limits:** bounded pagination, deterministic ordering, batch sizes, oversized result materialization, N+1 network calls and large memory allocations.
- **Contracts:** parameterized SQL, constraints, null/unique/foreign-key handling, schema migrations, existing-data and rolling-version compatibility.

## Locks, transactions and distributed data integrity

- Check atomicity and whether a partial failure violates a business invariant. Keep transactions reasonably scoped; avoid remote I/O under DB locks without necessity.
- Inspect row access and lock **acquisition order**, isolation levels, lost updates, optimistic/pessimistic locks, lock waits and deadlock risk. Where retries are justified, use bounded full-transaction retry with correct idempotency instead of masking every database error.
- In queues/distributed services: duplicate/out-of-order messages, retry ownership, idempotency keys, transactional outbox/compensation (only if relevant), failure recovery and reconciliations.

## Cache correctness and lifetime

- Identify the source of truth and allowed staleness; inspect cache-aside/write/invalidation strategy for races with DB commits, concurrent refresh and stale re-population.
- Check key namespace and tenant isolation, TTL, bounded cardinality, eviction, hot-key pressure, cache stampede, negative caching and unhealthy-dependency fallback when relevant.
- Prefer existing cache infrastructure and business-consistent policies. **Do not suggest introducing Redis, a distributed lock or more indexes merely to satisfy generic "best practices".**

## Evidence threshold and human decisions

An actionable finding states query/code path + actual or clearly predicted failure mechanism + data/workload assumptions + user/system impact + smallest valid repair. Distinguish **measured** N+1 counts from theoretical concerns. A necessary latency-versus-consistency or data retention product trade-off may require human decision; routine query tuning usually does not.

**Example:** "The updated order list performs a child lookup for each row; at 200 rows the trace shows 201 SQL calls. This exceeds the existing budget; batch child IDs and preserve ordering." This is useful. "Add indexes because indexes are good" is not.

## Official references
- [PostgreSQL — Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
- [PostgreSQL — Explicit Locking and Deadlocks](https://www.postgresql.org/docs/current/explicit-locking.html)
- [Redis — Key Eviction](https://redis.io/docs/latest/develop/reference/eviction/)
- [MySQL 8.4 — Indexes](https://dev.mysql.com/doc/refman/8.4/en/mysql-indexes.html)

Do not apply a particular vendor's internals to a different DB product without verifying its behavior.
