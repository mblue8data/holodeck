# PostgreSQL Cheatsheet (MySQL → PostgreSQL Mapping)

## psql Connection

```bash
# From terminal
psql -h localhost -p 5432 -U user -d mydb

# Inside container
docker exec -it holodeck-postgres-1 psql -U user -d mydb

# Connection string
postgresql://user:pass@localhost:5432/mydb
```

---

## Command Mapping

| MySQL | PostgreSQL (psql) |
|---|---|
| `SHOW DATABASES;` | `\l` |
| `USE mydb;` | `\c mydb` |
| `SHOW TABLES;` | `\dt` |
| `DESCRIBE tablename;` | `\d tablename` |
| `SHOW COLUMNS FROM tablename;` | `\d tablename` |
| `SHOW INDEXES FROM tablename;` | `\di` |
| `SHOW CREATE TABLE tablename;` | `\d+ tablename` |
| `SHOW PROCESSLIST;` | `SELECT * FROM pg_stat_activity;` |
| `SHOW VARIABLES;` | `SHOW ALL;` |
| `EXIT` / `QUIT` | `\q` |

---

## Useful psql Meta-Commands

```
\?          -- all psql meta-commands
\l          -- list databases
\c dbname   -- switch database
\dt         -- list tables in current schema
\dt *.      -- list tables in all schemas
\d name     -- describe table, view, or sequence
\d+ name    -- describe with extra detail
\dn         -- list schemas
\du         -- list users/roles
\di         -- list indexes
\timing     -- toggle query execution timing
\e          -- open last query in $EDITOR
\q          -- quit
```

---

## Common SQL (works in psql and GUI tools)

```sql
-- List all tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

-- List all schemas
SELECT schema_name FROM information_schema.schemata;

-- List all columns in a table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'tablename';

-- List active connections
SELECT * FROM pg_stat_activity;

-- List all users
SELECT usename FROM pg_user;

-- Database size
SELECT pg_size_pretty(pg_database_size('mydb'));

-- Table size
SELECT pg_size_pretty(pg_total_relation_size('tablename'));
```

> **Note:** Backslash commands (`\dt`, `\d`, etc.) are psql-shell only.
> Use the SQL equivalents above in GUI tools like DBeaver, TablePlus, or pgAdmin.
