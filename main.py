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

def get_weekly_entries() -> list:
    """Return all entries for the current week as dicts with parsed timestamps."""
    today = date.today()
    start = start_of_week(today)
    end = start + timedelta(days=7)
    raw_entries = load_data()
    entries = []
    for e in raw_entries:
        ts = datetime.fromisoformat(e["timestamp"])
        exit_ts = e.get("exit_timestamp")
        if exit_ts:
            exit_ts = datetime.fromisoformat(exit_ts)
        if start <= ts < end:
            entries.append({**e, "timestamp": ts, "exit_timestamp": exit_ts})
    return entries

def get_today_open_entries() -> list:
    today = date.today()
    entries = load_data()
    open_entries = []
    for idx, e in enumerate(entries):
        ts = datetime.fromisoformat(e["timestamp"])
        if ts.date() == today and not e.get("exit_timestamp"):
            open_entries.append((idx, e))
    return open_entries

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/entry')
def entry_page():
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
        "timestamp": datetime.now().isoformat(),
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
    return redirect('/thanks-entry')

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


    headers = [
        "Date d'arrivée",
        "Heure d'arrivée",
        "Sortie",
        "Nom",
        "Prénom",
        "Entreprise",
        "Motif",
        "Hôte",
        "Signature",
    ]
    widths = [30, 25, 25, 30, 30, 40, 40, 30, 40]
    table_width = sum(widths)

    pdf.set_font("helvetica", "B", 10)
    x_start = (pdf.w - table_width) / 2
    pdf.set_x(x_start)
    for h, w in zip(headers, widths):
        pdf.cell(w, 10, h, border=1, align="C")
    pdf.ln()

    pdf.set_font('helvetica', '', 9)
    for e in entries:
        exit_time = (
            e['exit_timestamp'].strftime('%Y-%m-%d %H:%M')
            if e.get('exit_timestamp')
            else ''
        )
        values = [
            e['timestamp'].strftime('%Y-%m-%d'),
            e['timestamp'].strftime('%H:%M'),
            exit_time,
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


@app.route('/exit', methods=['GET', 'POST'])
def exit_page():
    if request.method == 'POST':
        entry_id = int(request.form.get('entry_id'))
        entries = load_data()
        if 0 <= entry_id < len(entries):
            entries[entry_id]['exit_timestamp'] = datetime.now().isoformat()
            save_data(entries)
        return redirect('/thanks-exit')

    open_entries = get_today_open_entries()
    return render_template('exit.html', entries=open_entries)


@app.route('/thanks-entry')
def thanks_entry():
    return render_template('message.html', message='Bonne visite')


@app.route('/thanks-exit')
def thanks_exit():
    return render_template('message.html', message='Au revoir, bonne journée')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
