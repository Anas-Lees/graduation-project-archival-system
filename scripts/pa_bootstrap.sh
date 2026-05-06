#!/usr/bin/env bash
# One-shot PythonAnywhere bootstrap for GPAS.
# Run this *once* in a PythonAnywhere Bash console after cloning the repo.
#
# Usage (from the repo root, e.g. ~/graduation-project-archival-system):
#   bash scripts/pa_bootstrap.sh
#
# It will:
#   1. Create a Python 3.11 virtualenv called "gpas-venv" via mkvirtualenv (PA-provided)
#   2. Install requirements
#   3. Compile translations
#   4. Generate a strong SECRET_KEY and write it to .env
#   5. Initialise the database and seed demo data

set -euo pipefail

cd "$(dirname "$0")/.."
PROJECT_ROOT="$(pwd)"
VENV_NAME="gpas-venv"

echo "GPAS — PythonAnywhere bootstrap"
echo "  project root: $PROJECT_ROOT"
echo

# --- 1. virtualenv -----------------------------------------------------------
if ! command -v mkvirtualenv >/dev/null 2>&1; then
  echo "ERROR: mkvirtualenv not found. Are you running this on PythonAnywhere?"
  echo "If running locally, replace this script with:"
  echo "  python3.11 -m venv venv && source venv/bin/activate"
  exit 1
fi

if workon | grep -qx "$VENV_NAME"; then
  echo "→ virtualenv '$VENV_NAME' already exists, activating"
else
  echo "→ creating virtualenv '$VENV_NAME' (python3.11)"
  mkvirtualenv --python=/usr/bin/python3.11 "$VENV_NAME"
fi
source ~/.virtualenvs/"$VENV_NAME"/bin/activate

# --- 2. dependencies ---------------------------------------------------------
echo "→ installing requirements"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# --- 3. translations ---------------------------------------------------------
echo "→ compiling translations"
pybabel compile -d translations >/dev/null 2>&1 || python scripts/fill_translations.py

# --- 4. .env -----------------------------------------------------------------
ENV_FILE="$PROJECT_ROOT/.env"
if [ ! -f "$ENV_FILE" ]; then
  SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(48))")
  cat > "$ENV_FILE" <<EOF
# GPAS production environment — created by pa_bootstrap.sh
SECRET_KEY=$SECRET_KEY
FLASK_HTTPS=1
EOF
  echo "→ wrote $ENV_FILE with a fresh SECRET_KEY"
else
  echo "→ .env already exists; leaving it alone"
fi

# --- 5. database & seed ------------------------------------------------------
echo "→ initialising database"
python scripts/init_db.py
echo "→ seeding demo data"
python scripts/seed.py

# --- summary -----------------------------------------------------------------
echo
echo "✓ Bootstrap complete."
echo
echo "Next steps inside the PythonAnywhere dashboard:"
echo "  1. Web → Add a new web app → Manual config → Python 3.11"
echo "  2. Source code:        $PROJECT_ROOT"
echo "  3. Working directory:  $PROJECT_ROOT"
echo "  4. Virtualenv:         /home/\$USER/.virtualenvs/$VENV_NAME"
echo "  5. WSGI configuration: paste the contents of scripts/pa_wsgi.py"
echo "  6. Static files: URL '/static/' → Path '$PROJECT_ROOT/app/static'"
echo "  7. Click the green Reload button"
echo
echo "Login credentials:"
echo "  student@aou.edu.kw / Student123!"
echo "  doc@aou.edu.kw     / Doctor123!"
