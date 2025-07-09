from datetime import datetime, date, timedelta
import io

from flask import Flask, render_template, request, redirect, send_file
import json
import base64
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

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/entree')
def entree():
    return render_template('entree.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/visite')
def visite():
    return render_template('visite.html')


@app.route('/sortie')
def sortie():
    today = date.today()
    entries = []
    for e in load_data():
        ts = datetime.fromisoformat(e['timestamp'])
        if ts.date() == today and not e.get('exit_timestamp'):
            entries.append({**e, 'timestamp': ts})
    return render_template('sortie.html', entries=entries)


@app.route('/record_exit', methods=['POST'])
def record_exit():
    ts = request.form.get('timestamp')
    entries = load_data()
    for e in entries:
        if e['timestamp'] == ts and not e.get('exit_timestamp'):
            e['exit_timestamp'] = datetime.utcnow().isoformat()
            break
    save_data(entries)
    return redirect('/au_revoir')


@app.route('/au_revoir')
def au_revoir():
    return render_template('au_revoir.html')


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
        "signature": request.form.get("signature"),
        "exit_timestamp": None
    }
    entries.append(entry)
    save_data(entries)
    return redirect('/visite')

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

    pdf = FPDF(orientation="L")
    pdf.add_page()

    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10,
             f"Registre de la semaine du {start.date()} au {end.date()}",
             ln=1, align="C")


    headers = [
        "Date", "Nom", "Prénom", "Entreprise",
        "Motif", "Hôte", "Signature", "Sortie"
    ]
    widths = [30, 30, 30, 40, 40, 30, 40, 30]
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
        for v, w in zip(values, widths[:6]):
            pdf.cell(w, row_height, str(v), border=1)
        sig_x = pdf.get_x()
        sig_y = pdf.get_y()
        pdf.cell(widths[6], row_height, "", border=1)
        if e.get('signature'):
            try:
                b64 = e['signature'].split(',')[1] if ',' in e['signature'] else e['signature']
                img_data = base64.b64decode(b64)
                pdf.image(io.BytesIO(img_data), x=sig_x+2, y=sig_y+2,
                          w=widths[6]-4, h=row_height-4, type="PNG")
            except Exception:
                pass
        exit_str = ""
        if e.get('exit_timestamp'):
            try:
                exit_dt = datetime.fromisoformat(e['exit_timestamp'])
                exit_str = exit_dt.strftime('%Y-%m-%d %H:%M')
            except Exception:
                exit_str = str(e['exit_timestamp'])
        pdf.cell(widths[7], row_height, exit_str, border=1)
        pdf.ln()


    pdf_bytes = pdf.output(dest='S')

    return send_file(io.BytesIO(pdf_bytes), download_name='registre.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
