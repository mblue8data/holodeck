// Holodeck schema — edit this file and run `atlas schema apply` to migrate

schema "raw" {}
schema "staging" {}
schema "marts" {}

// --- raw layer ---

table "customers" {
  schema = schema.raw
  column "id"         { type = serial }
  column "name"       { type = varchar(100) }
  column "email"      { type = varchar(100) }
  column "country"    { type = varchar(50) }
  column "created_at" { type = timestamp; default = sql("now()") }
  primary_key { columns = [column.id] }
}

table "transactions" {
  schema = schema.raw
  column "id"         { type = serial }
  column "user_id"    { type = int }
  column "amount"     { type = numeric(10, 2) }
  column "currency"   { type = varchar(3) }
  column "status"     { type = varchar(20) }
  column "created_at" { type = timestamp; default = sql("now()") }
  primary_key { columns = [column.id] }
  foreign_key "fk_customer" {
    columns     = [column.user_id]
    ref_columns = [table.customers.column.id]
    on_delete   = NO_ACTION
  }
}

// --- staging layer (views managed by dbt, placeholders here) ---

// --- marts layer ---

table "customer_summary" {
  schema = schema.marts
  column "customer_id"       { type = int }
  column "name"              { type = varchar(100) }
  column "country"           { type = varchar(50) }
  column "total_transactions"{ type = int }
  column "total_spent"       { type = numeric(12, 2) }
  column "last_transaction_at" { type = timestamp; null = true }
  primary_key { columns = [column.customer_id] }
}
