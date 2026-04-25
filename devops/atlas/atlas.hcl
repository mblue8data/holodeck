// Atlas project config — connection URL for the local Postgres instance

env "local" {
  src = "file://schema.hcl"
  url = "postgres://user:pass@postgres:5432/mydb?search_path=public&sslmode=disable"
  dev = "docker://postgres/15/dev"
}
