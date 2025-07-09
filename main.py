from datetime import datetime, date, timedelta
import io

from flask import Flask, render_template, request, redirect, send_file
import json
from fpdf import FPDF

app = Flask(__name__)
DATA_FILE = "visitors.json"

def load_data() -> list:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(entries: list) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def start_of_week(dt: date) -> datetime:
    start = dt - timedelta(days=dt.weekday())
    return datetime.combine(start, datetime.min.time())

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    entries = load_data()
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "first_name": request.form.get("first_name"),
        "last_name": request.form.get("last_name"),
        "company": request.form.get("company"),
        "reason": request.form.get("reason"),
        "host": request.form.get("host"),
        "signature": request.form.get("signature")
    }
    entries.append(entry)
    save_data(entries)
    return redirect('/')

@app.route('/export')
def export_pdf():
    today = date.today()
    start = start_of_week(today)
    end = start + timedelta(days=7)
    raw_entries = load_data()
    entries = []
    for e in raw_entries:
        ts = datetime.fromisoformat(e["timestamp"])
        if start <= ts < end:
            entries.append({**e, "timestamp": ts})

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Registre de la semaine du {start.date()} au {end.date()}", ln=True)

    headers = ["Date", "Nom", "Prénom", "Entreprise", "Motif", "Hôte"]
    widths = [30, 30, 30, 40, 40, 30]

    pdf.set_font('Arial', 'B', 10)
    for h, w in zip(headers, widths):
        pdf.cell(w, 10, h, border=1)
    pdf.ln()

    pdf.set_font('Arial', '', 9)
    for e in entries:
        values = [
            e['timestamp'].strftime('%Y-%m-%d %H:%M'),
            e['last_name'],
            e['first_name'],
            e.get('company', ''),
            e.get('reason', ''),
            e.get('host', '')
        ]
        for v, w in zip(values, widths):
            pdf.cell(w, 10, str(v), border=1)
        pdf.ln()

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return send_file(io.BytesIO(pdf_bytes), download_name='registre.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
