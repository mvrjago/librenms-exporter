from flask import (
    Flask,
    render_template,
    request,
    send_file,
    redirect,
    url_for,
    session,
    send_from_directory,
    flash,
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    UserMixin,
)

from werkzeug.security import check_password_hash

from datetime import datetime
import os
import uuid
import json

from rrd_tools import (
    cpu_exporter,
    memory_exporter,
    storage_exporter,
)

import config


app = Flask(__name__)

app.secret_key = config.SECRET_KEY
app.permanent_session_lifetime = (
    config.PERMANENT_SESSION_LIFETIME
)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

USERS_FILE = os.path.join(
    BASE_DIR,
    "users.json"
)

class User(UserMixin):
    def __init__(self, username):
        self.id = username


def load_users():
    try:
        with open(
            USERS_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except FileNotFoundError:
        return {}

    except json.JSONDecodeError:
        return {}


@login_manager.user_loader
def load_user(user_id):
    users = load_users()

    if user_id in users:
        return User(user_id)

    return None

@app.before_request
def make_session_permanent():
    session.permanent = True
    session.modified = True

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        users = load_users()

        username = request.form[
            "username"
        ].strip()

        password = request.form[
            "password"
        ]

        user_data = users.get(username)

        if (
            user_data
            and check_password_hash(
                user_data["password_hash"],
                password,
            )
        ):
            user = User(username)

            login_user(user)

            return redirect(
                url_for("index")
            )

        flash(
            "Username atau password salah",
            "danger",
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "login.html"
    )


@app.route(
    "/logout",
    methods=["GET", "POST"]
)
@login_required
def logout():

    logout_user()

    session.clear()

    return redirect(
        url_for("login")
    )

@app.route(
    "/",
    methods=["GET", "POST"]
)
@login_required
def index():

    if request.method == "POST":

        rrd_type = request.form.get(
            "rrd_type"
        )

        start_date = request.form.get(
            "start_date"
        )

        end_date = request.form.get(
            "end_date"
        )

        try:

            if rrd_type in [
                "cpu",
                "memory",
            ]:

                start_ts = int(
                    datetime.strptime(
                        start_date,
                        "%Y-%m-%d",
                    ).timestamp()
                )

                end_ts = int(
                    datetime.strptime(
                        end_date,
                        "%Y-%m-%d",
                    ).timestamp()
                )

            else:

                start_ts = None
                end_ts = None

        except Exception as e:

            return (
                f"Invalid date format: {e}",
                400,
            )

        filename = (
            f"{rrd_type}_usage_"
            f"{uuid.uuid4().hex}.csv"
        )

        os.makedirs(
            config.EXPORT_TEMP_DIR,
            exist_ok=True,
        )

        output_path = os.path.join(
            config.EXPORT_TEMP_DIR,
            filename,
        )

        try:

            if rrd_type == "cpu":

                cpu_exporter.generate_csv(
                    output_path,
                    start_ts,
                    end_ts,
                )

            elif rrd_type == "memory":

                memory_exporter.generate_csv(
                    output_path,
                    start_ts,
                    end_ts,
                )

            elif rrd_type == "storage":

                storage_exporter.generate_csv(
                    output_path,
                )

            else:

                return (
                    "Invalid RRD type",
                    400,
                )

        except Exception as e:

            return (
                f"Error generating CSV: {e}",
                500,
            )

        return send_file(
            output_path,
            as_attachment=True,
        )

    return render_template(
        "index.html"
    )

@app.route("/favicon.ico")
def favicon():

    return send_from_directory(
        os.path.join(
            app.root_path,
            "static",
        ),
        "favicon.ico",
        mimetype=(
            "image/vnd.microsoft.icon"
        ),
    )

if __name__ == "__main__":

    app.run(
        host=config.APP_HOST,
        port=config.APP_PORT,
        debug=config.APP_DEBUG,
    )