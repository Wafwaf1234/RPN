from datetime import datetime, date, timedelta
import io

from flask import Flask, render_template, request, redirect, send_file
import json
import base64
from fpdf import FPDF

from fpdf.enums import XPos, YPos

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

def get_weekly_entries() -> list:
    """Return all entries for the current week as dicts with parsed timestamps."""
    today = date.today()
    start = start_of_week(today)
    end = start + timedelta(days=7)
    raw_entries = load_data()
    entries = []
    for e in raw_entries:
        ts = datetime.fromisoformat(e["timestamp"])
        if start <= ts < end:
            entries.append({**e, "timestamp": ts})
    return entries

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/entries')
def entries():
    """Display this week's entries in a simple table."""
    data = get_weekly_entries()
    return render_template('entries.html', entries=data)


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
    entries = get_weekly_entries()
    if not entries:
        # No entries this week, still compute start and end for header
        today = date.today()
        start = start_of_week(today)
        end = start + timedelta(days=7)
    else:
        start = start_of_week(entries[0]["timestamp"].date())
        end = start + timedelta(days=7)

    pdf = FPDF(orientation="L")
    pdf.add_page()

    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10,
             f"Registre de la semaine du {start.date()} au {end.date()}",
             ln=1, align="C")


    headers = ["Date", "Nom", "Prénom", "Entreprise", "Motif", "Hôte", "Signature"]
    widths = [30, 30, 30, 40, 40, 30, 40]
    table_width = sum(widths)

    pdf.set_font("helvetica", "B", 10)
    x_start = (pdf.w - table_width) / 2
    pdf.set_x(x_start)
    for h, w in zip(headers, widths):
        pdf.cell(w, 10, h, border=1, align="C")
    pdf.ln()

    pdf.set_font('helvetica', '', 9)
    for e in entries:
        values = [
            e['timestamp'].strftime('%Y-%m-%d %H:%M'),
            e['last_name'],
            e['first_name'],
            e.get('company', ''),
            e.get('reason', ''),
            e.get('host', '')
        ]
        row_height = 20
        pdf.set_x(x_start)
        for v, w in zip(values, widths[:-1]):
            pdf.cell(w, row_height, str(v), border=1)
        sig_x = pdf.get_x()
        sig_y = pdf.get_y()
        pdf.cell(widths[-1], row_height, "", border=1)
        if e.get('signature'):
            try:
                b64 = e['signature'].split(',')[1] if ',' in e['signature'] else e['signature']
                img_data = base64.b64decode(b64)
                pdf.image(io.BytesIO(img_data), x=sig_x+2, y=sig_y+2,
                          w=widths[-1]-4, h=row_height-4, type="PNG")
            except Exception:
                pass
        pdf.ln()


    pdf_bytes = pdf.output(dest='S')

    return send_file(io.BytesIO(pdf_bytes), download_name='registre.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
