from pathlib import Path
import json
import joblib
import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parent

NOTEBOOK_PATH = ROOT / "notebook" / "analysis_and_prediction.ipynb"
OUTPUT_NOTEBOOK = ROOT / "notebook" / "artifact_generation_executed.ipynb"
MODEL_DIR = ROOT / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 60)
print("Financial Market ML Artifact Generator")
print("=" * 60)

print(f"Project root: {ROOT}")
print(f"Notebook:     {NOTEBOOK_PATH}")
print(f"Model dir:    {MODEL_DIR}")


if not NOTEBOOK_PATH.exists():
    raise FileNotFoundError(
        f"Notebook not found: {NOTEBOOK_PATH}"
    )


# ------------------------------------------------------------
# Load notebook
# ------------------------------------------------------------

with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
    notebook = nbformat.read(f, as_version=4)


# ------------------------------------------------------------
# Execute notebook from notebook directory
# ------------------------------------------------------------

client = NotebookClient(
    notebook,
    timeout=600,
    kernel_name="python3",
)

client.execute(
    cwd=str(NOTEBOOK_PATH.parent)
)


# ------------------------------------------------------------
# Verify execution
# ------------------------------------------------------------

errors = []

for index, cell in enumerate(notebook.cells):
    for output in cell.get("outputs", []):
        if output.get("output_type") == "error":
            errors.append({
                "cell": index,
                "error": output.get("ename"),
                "message": output.get("evalue"),
            })


if errors:
    print("\nNotebook execution failed:\n")

    for error in errors:
        print(
            f"Cell {error['cell']}: "
            f"{error['error']} - {error['message']}"
        )

    raise RuntimeError(
        "Notebook execution failed. "
        "No model artifacts were created."
    )


# ------------------------------------------------------------
# Save executed notebook for verification
# ------------------------------------------------------------

with open(OUTPUT_NOTEBOOK, "w", encoding="utf-8") as f:
    nbformat.write(notebook, f)


print("\nNotebook executed successfully.")
print(f"Executed notebook saved to: {OUTPUT_NOTEBOOK}")


# ------------------------------------------------------------
# Locate trained model/scaler variables
# ------------------------------------------------------------

# The notebook execution environment is isolated inside nbclient,
# so this script does not directly receive Python variables.
#
# Therefore we extract the trained model/scaler by adding a small
# artifact-saving cell to the notebook execution itself.


artifact_cell = nbformat.v4.new_code_cell(
    """
from pathlib import Path
import json
import joblib

ROOT = Path.cwd().parent
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "market_model.keras"
SCALER_PATH = MODEL_DIR / "feature_scaler.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

model.save(MODEL_PATH)
joblib.dump(scaler, SCALER_PATH)

metadata = {
    "model_type": "TensorFlow/Keras Dense Neural Network",
    "target": "next_trading_day_close",
    "features": FEATURES,
    "feature_count": len(FEATURES),
    "training_samples": int(len(X_train)),
    "testing_samples": int(len(X_test)),
    "baseline_mae": float(baseline_mae),
    "baseline_rmse": float(baseline_rmse),
    "baseline_r2": float(baseline_r2),
    "model_mae": float(mae),
    "model_rmse": float(rmse),
    "model_r2": float(r2),
}

with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4)

print("MODEL_SAVED:", MODEL_PATH)
print("SCALER_SAVED:", SCALER_PATH)
print("METADATA_SAVED:", METADATA_PATH)
"""
)

notebook.cells.append(artifact_cell)

client = NotebookClient(
    notebook,
    timeout=600,
    kernel_name="python3",
)

client.execute(
    cwd=str(NOTEBOOK_PATH.parent)
)


print("\n" + "=" * 60)
print("Artifact generation complete")
print("=" * 60)


for path in [
    MODEL_DIR / "market_model.keras",
    MODEL_DIR / "feature_scaler.joblib",
    MODEL_DIR / "model_metadata.json",
]:
    if path.exists():
        print(f"[OK] {path.name} ({path.stat().st_size:,} bytes)")
    else:
        print(f"[MISSING] {path.name}")