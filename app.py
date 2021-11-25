import os
import pathlib
import requests
from pip._vendor import cachecontrol
import google
from google.oauth2 import id_token

from flask import Flask, render_template, redirect, request, url_for, session
from werkzeug.datastructures import cache_property
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from authlib.integrations.flask_client import OAuth

load_dotenv()

app = Flask(__name__)
app.secret_key = f"{os.getenv('secret_key')}"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "718120522137-o13a98t0jrn28i3lp1rotl2uspbjsvqu.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/authorize"
)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{os.getenv("password")}@localhost/postgres'
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
    email = dict(session).get("email",None)
    print(email)
    return render_template("index.html")

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        sno = request.form['sno']
        name = request.form['name']
        profn = request.form['profn']

    test_db = Table(sno, name, profn)
    print(test_db)
    db.session.add(test_db)
    db.session.commit()

    return render_template('success.html')

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/authorize")
def authorize():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)

    credentials = flow.credentials
    request_session = requests.session()
    chached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=chached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    
    return id_info

# @app.route("/callback")
# def callback():
#     pass

# @app.route("/index")
# def index():
#     pass

# @app.route("/protected_area")
# def protected_area():
#     pass

if __name__ == "__main__":
    app.run(debug=True)