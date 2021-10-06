import os

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{os.getenv("password")}@localhost/test'

db = SQLAlchemy(app)


class Table(db.Model):
    __tablename__ = "test_db"
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    profn = db.Column(db.String(90))

    def __init__(self, sno, name, profn):
        self.sno = sno
        self.name = name
        self.profn = profn


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        sno = request.form['sno']
        name = request.form['name']
        profn = request.form['profn']

    test_db = Table(sno, name, profn)
    db.session.add(test_db)
    db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)