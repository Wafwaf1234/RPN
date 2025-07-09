from datetime import datetime, date, timedelta
import base64
import io

from flask import Flask, render_template, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from fpdf import FPDF

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visitors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    company = db.Column(db.String(100))
    reason = db.Column(db.String(200))
    host = db.Column(db.String(100))
    signature = db.Column(db.Text)  # base64 data URL

def start_of_week(dt: date) -> datetime:
    start = dt - timedelta(days=dt.weekday())
    return datetime.combine(start, datetime.min.time())

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = Visitor(
        first_name=request.form.get('first_name'),
        last_name=request.form.get('last_name'),
        company=request.form.get('company'),
        reason=request.form.get('reason'),
        host=request.form.get('host'),
        signature=request.form.get('signature')
    )
    db.session.add(data)
    db.session.commit()
    return redirect('/')

@app.route('/export')
def export_pdf():
    today = date.today()
    start = start_of_week(today)
    end = start + timedelta(days=7)
    entries = Visitor.query.filter(Visitor.timestamp >= start, Visitor.timestamp < end).all()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Registre de la semaine du {start.date()} au {end.date()}", ln=True)

    pdf.set_font('Arial', '', 10)
    for e in entries:
        line = f"{e.timestamp:%Y-%m-%d %H:%M} | {e.first_name} {e.last_name} | {e.company} | {e.reason} | {e.host}"
        pdf.multi_cell(0, 10, line)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return send_file(io.BytesIO(pdf_bytes), download_name='registre.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000)
