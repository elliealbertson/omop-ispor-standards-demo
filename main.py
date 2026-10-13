import os, runpy, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
MODULES_DIR = REPO_ROOT / "modules"
VENV_DIR = REPO_ROOT / ".venv"
VENV_PYTHON = VENV_DIR / "bin" / "python"
if Path(sys.prefix).resolve() != VENV_DIR.resolve():
    if not VENV_PYTHON.exists():
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", "-r", str(REPO_ROOT / "requirements.txt")], check=True)
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), *sys.argv])
sys.path.insert(0, str(MODULES_DIR))
print("Running omop_query.py: pull drug exposure records from BigQuery")
runpy.run_path(str(MODULES_DIR / "omop_query.py"))
print("Running data_quality.py: profile records and report data quality")
runpy.run_path(str(MODULES_DIR / "data_quality.py"))
print("Running ispor_adherence.py: measure statin adherence by days covered")
runpy.run_path(str(MODULES_DIR / "ispor_adherence.py"))
