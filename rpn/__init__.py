from flask import Flask
from pathlib import Path

app = Flask(__name__, template_folder='templates')

# Path to data file (visitors.json) at repository root
BASE_DIR = Path(__file__).resolve().parent.parent
app.config['DATA_FILE'] = BASE_DIR / 'visitors.json'

from . import routes  # noqa: E402
