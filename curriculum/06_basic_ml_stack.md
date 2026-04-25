# Curriculum: ML Tracking with MLflow and Dagster

**Sequence:** `basic_ml_stack`
**Level:** Intermediate
**Stack:** MLflow · Dagster

## What You Will Learn
- Tracking ML experiments with MLflow (parameters, metrics, artifacts)
- Comparing runs to find the best model
- Registering a model and managing versions
- Wiring MLflow into a Dagster pipeline so training is orchestrated

## Prerequisites
- Python basics (functions, loops, imports)
- Basic understanding of what a machine learning model is
- `pip install mlflow scikit-learn pandas` in your local environment

## Start the Stack
```bash
./holo --load basic_ml_stack
```

| Service | URL |
|---------|-----|
| MLflow | http://localhost:5000 |
| Dagster | http://localhost:3010 |

---

## Module 1 — Your First MLflow Experiment

MLflow tracks experiments from your local machine — you don't need to be inside a container.

**Exercise 1.1 — Log a simple run**

Create a file `mlflow_hello.py` anywhere on your machine:
```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("holodeck-hello")

with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_param("epochs", 10)
    mlflow.log_metric("accuracy", 0.87)
    mlflow.log_metric("loss", 0.34)

print("Run logged. Open http://localhost:5000 to view it.")
```

```bash
python mlflow_hello.py
```

Open **http://localhost:5000** and find the run under `holodeck-hello`.

**Exercise 1.2 — Log multiple metrics over time**
```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("holodeck-hello")

with mlflow.start_run(run_name="training-loop"):
    mlflow.log_param("epochs", 20)
    for epoch in range(1, 21):
        accuracy = 0.5 + (epoch * 0.02)   # simulated improvement
        loss = 1.0 - (epoch * 0.04)
        mlflow.log_metric("accuracy", accuracy, step=epoch)
        mlflow.log_metric("loss", loss, step=epoch)
```

In MLflow UI, click the run and view the **accuracy** and **loss** charts over steps.

---

## Module 2 — Track a Real Model

**Exercise 2.1 — Train and track a fraud classifier**

Create `train_fraud_model.py`:
```python
import mlflow
import mlflow.sklearn
import pandas as pd
import duckdb
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("fraud-detection")

# Load data
con = duckdb.connect()
df = con.execute("SELECT * FROM 'data/raw/fraud_data01.parquet'").df()

# Simple feature selection — adjust to match your schema columns
features = ['transaction_amount', 'age']  # update based on actual columns
target = 'is_fraud'

X = df[features].fillna(0)
y = df[target].astype(int)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Experiment with different parameters
for n_estimators in [50, 100, 200]:
    with mlflow.start_run(run_name=f"rf-n{n_estimators}"):
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("features", features)

        model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        mlflow.log_metric("accuracy",  accuracy_score(y_test, preds))
        mlflow.log_metric("precision", precision_score(y_test, preds))
        mlflow.log_metric("recall",    recall_score(y_test, preds))
        mlflow.log_metric("f1",        f1_score(y_test, preds))

        mlflow.sklearn.log_model(model, "model")

        print(f"n_estimators={n_estimators}  f1={f1_score(y_test, preds):.3f}")
```

```bash
python train_fraud_model.py
```

---

## Module 3 — Compare Runs in the UI

**Exercise 3.1 — Compare experiments**
- Open **http://localhost:5000** → `fraud-detection` experiment
- Select all three runs → click **Compare**
- Sort by `f1` descending — identify the best model

**Exercise 3.2 — Read the artifacts**
- Click the best run
- Navigate to **Artifacts** → `model/` → read `MLmodel` file
- This file describes the model flavor, Python version, and dependencies

**Exercise 3.3 — Add tags**

Add to your training script before `mlflow.start_run`:
```python
tags = {"team": "holodeck", "dataset": "fraud_v1", "env": "dev"}
```

Inside the run:
```python
mlflow.set_tags(tags)
```

Tags let you filter and organize runs across experiments.

---

## Module 4 — Model Registry

The registry is where you promote a run from an experiment into a named, versioned model.

**Exercise 4.1 — Register a model**
- Open the best run in the UI
- Click **Register Model** → name it `fraud-classifier`
- Set the version stage to **Staging**

**Exercise 4.2 — Load a registered model**
```python
import mlflow.sklearn

mlflow.set_tracking_uri("http://localhost:5000")

model = mlflow.sklearn.load_model("models:/fraud-classifier/Staging")
print(model)
```

**Exercise 4.3 — Promote to Production**
- In the UI, find the model version under **Models** → `fraud-classifier`
- Transition it from **Staging** → **Production**
- Update the load call: `"models:/fraud-classifier/Production"`

---

## Module 5 — Orchestrate with Dagster

Integrate the training job into Dagster so it runs on a schedule.

**Exercise 5.1 — Add an MLflow asset to Dagster**

Edit `dagster/definitions.py`:
```python
import subprocess
from dagster import asset, Definitions, ScheduleDefinition, define_asset_job

@asset
def raw_fraud_data():
    """Represents the fraud parquet file on disk."""
    return {"path": "data/raw/fraud_data01.parquet"}

@asset(deps=[raw_fraud_data])
def fraud_model():
    """Trains the fraud classifier and logs to MLflow."""
    result = subprocess.run(
        ["python3", "train_fraud_model.py"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Training failed:\n{result.stderr}")
    return {"status": "trained"}

training_job = define_asset_job("train_fraud_model_job", selection="*")

weekly_schedule = ScheduleDefinition(
    job=training_job,
    cron_schedule="0 2 * * 1",  # Monday 2am
)

defs = Definitions(
    assets=[raw_fraud_data, fraud_model],
    schedules=[weekly_schedule],
)
```

Restart Dagster and verify the `fraud_model` asset appears in the UI.

**Exercise 5.2 — Trigger a manual run**
- In Dagster UI → **Assets** → **Materialize All**
- Watch the run log — it should trigger training and log to MLflow
- Open MLflow and verify a new run appeared

---

## Checkpoint

Before moving on, you should be able to:
- [ ] Log parameters, metrics, and a model artifact to MLflow
- [ ] Compare multiple runs and identify the best by a metric
- [ ] Register a model and transition it through Staging → Production
- [ ] Load a model from the registry by name and stage
- [ ] Trigger a training job from Dagster

## Next Steps
- **`full_stack`** — serve predictions from a registered model inside the full data pipeline
- **`duckdb_lab`** — use DuckDB for feature engineering before training
