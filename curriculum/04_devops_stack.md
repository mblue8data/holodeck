# Curriculum: DevOps & DataOps

**Sequence:** `devops_stack`
**Level:** Intermediate
**Stack:** Postgres · LocalStack · Terraform · Atlas

## What You Will Learn
- Infrastructure as Code (IaC) with Terraform against a local AWS environment
- Provisioning S3 data lake buckets and IAM roles without a cloud account
- Declarative schema management with Atlas
- The full DataOps loop: schema change → migration → verify

## Prerequisites
- Comfortable with SQL and Postgres
- Basic understanding of what AWS S3 and IAM are (no account needed)

## Start the Stack
```bash
./holo --load devops_stack
```

---

## Module 1 — Infrastructure as Code with Terraform

Terraform manages infrastructure the same way dbt manages SQL models — you declare the desired
state and the tool figures out what needs to change.

**How it works here:**
- LocalStack runs on port 4566 and emulates AWS services (S3, IAM, STS)
- Terraform configs in `devops/terraform/` are pre-configured to target LocalStack
- Your AWS credentials are fake (`test`/`test`) — LocalStack ignores real auth

**Exercise 1.1 — Initialize Terraform**
```bash
docker exec -it terraform sh
terraform init
```

Read the output — Terraform downloads the AWS provider and locks the version in
`.terraform.lock.hcl`. This lock file ensures everyone on the team uses the same provider version.

**Exercise 1.2 — Plan before you apply**
```bash
terraform plan
```

Read every line of the plan:
- `+` means create
- `-` means destroy
- `~` means modify in place

You should see 5 resources: 3 S3 buckets, 1 S3 versioning config, 1 IAM role, 1 IAM policy.

**Exercise 1.3 — Apply the infrastructure**
```bash
terraform apply
# Type 'yes' when prompted
```

**Exercise 1.4 — Verify with the AWS CLI against LocalStack**
```bash
# Still inside the terraform container
aws --endpoint-url=http://localstack:4566 s3 ls
```

You should see your three buckets: `holodeck-raw`, `holodeck-staging`, `holodeck-marts`.

---

## Module 2 — Modify Infrastructure

The real skill with Terraform is making safe changes to existing infrastructure.

**Exercise 2.1 — Add a new bucket**

Open `devops/terraform/main.tf` and add:
```hcl
resource "aws_s3_bucket" "archive" {
  bucket = "${var.project}-archive"
}
```

```bash
terraform plan   # should show 1 resource to add, 0 to change, 0 to destroy
terraform apply
aws --endpoint-url=http://localstack:4566 s3 ls
```

**Exercise 2.2 — Understand state**
```bash
terraform show          # human-readable current state
terraform state list    # list all managed resources
```

Terraform state is what lets it know what already exists. Never edit `.tfstate` by hand.

**Exercise 2.3 — Destroy and rebuild**
```bash
terraform destroy       # removes everything Terraform created
terraform apply         # recreates it from scratch
```

This is the power of IaC — your infrastructure is fully reproducible from code.

**Exercise 2.4 — Add lifecycle protection**

In a real environment, you never want to accidentally delete a data bucket.
Add a lifecycle rule to `main.tf`:
```hcl
resource "aws_s3_bucket" "raw" {
  bucket = "${var.project}-raw"

  lifecycle {
    prevent_destroy = true
  }
}
```

Try to destroy it — Terraform will refuse. Remove the rule when done.

---

## Module 3 — Schema Migrations with Atlas

Atlas manages your database schema the way Terraform manages infrastructure:
you declare the desired state in `schema.hcl` and Atlas generates the migration SQL.

**Exercise 3.1 — Inspect the current schema**
```bash
docker exec -it atlas sh

# See what Atlas finds in the live database
atlas schema inspect \
  --url "postgres://user:pass@postgres:5432/mydb?sslmode=disable" \
  --schema raw,staging,marts
```

Compare this output to `schema.hcl` — they should match.

**Exercise 3.2 — Apply the baseline schema**
```bash
atlas schema apply --env local
```

Atlas will diff the desired state (`schema.hcl`) against the live database and
show you what SQL it would run. Type `yes` to apply.

**Exercise 3.3 — Make a schema change**

Open `devops/atlas/schema.hcl` and add a column to the `transactions` table:
```hcl
table "transactions" {
  schema = schema.raw
  // ... existing columns ...
  column "merchant" {
    type = varchar(100)
    null = true
  }
}
```

```bash
atlas schema diff --env local    # preview the ALTER TABLE statement
atlas schema apply --env local   # apply it
```

Verify in Postgres:
```bash
docker exec -it holodeck-postgres-1 psql -U user -d mydb -c "\d raw.transactions"
```

**Exercise 3.4 — Drop a column safely**

Remove the `merchant` column from `schema.hcl` and apply again. Atlas will generate
a `DROP COLUMN` statement. In production, dropping columns is dangerous (apps may still
reference them) — Atlas warns you. Practice reading those warnings.

---

## Module 4 — The Full DataOps Loop

Combine both tools in a realistic workflow.

**Scenario:** A new data source is coming in — payment processor data with a `processor_fee` field.
You need to provision storage for it AND update the schema.

**Step 1 — Provision a new S3 prefix (Terraform)**

Add to `main.tf`:
```hcl
resource "aws_s3_bucket_object" "payments_prefix" {
  bucket  = aws_s3_bucket.raw.bucket
  key     = "payments/"
  content = ""
}
```
```bash
terraform apply
```

**Step 2 — Update the schema (Atlas)**

Add to `schema.hcl` inside the `transactions` table:
```hcl
column "processor_fee" {
  type = numeric(8, 2)
  null = true
}
```
```bash
atlas schema apply --env local
```

**Step 3 — Verify the full chain**
```bash
# S3 prefix exists
aws --endpoint-url=http://localstack:4566 s3 ls s3://holodeck-raw/

# Schema column exists
docker exec -it holodeck-postgres-1 psql -U user -d mydb -c "\d raw.transactions"
```

This is the DevOps workflow: infrastructure change and schema change are both code-reviewed,
version-controlled, and reproducible.

---

## Checkpoint

Before moving on, you should be able to:
- [ ] Run `terraform init`, `plan`, and `apply` against LocalStack
- [ ] Read a Terraform plan and explain what each change means
- [ ] Inspect and apply a schema with Atlas
- [ ] Add a column via `schema.hcl` and verify the migration ran
- [ ] Explain why state files matter in Terraform

## Next Steps
- **`warehouse_stack`** — the schema you manage here is the one dbt models read from
- **`full_stack`** — connect all the pieces into a complete pipeline
