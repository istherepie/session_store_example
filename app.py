# -- coding: utf-8 --

# Imports
from os import environ
from base64 import b64encode

# Flask imports
from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask import make_response

# Redis (redis-py) imports
from redis import Redis
from redis import ConnectionPool

# Init flask
app = Flask(__name__)

# Create connection pool
pool = ConnectionPool(
    host=environ.get("REDIS_HOST") or "localhost",
    port=environ.get("REDIS_PORT") or 6379,
    db=environ.get("REDIS_DB") or 0
)


def generate_session(username):
    """

    :param string:
    :return:
    """

    # Init redis client
    client = Redis(connection_pool=pool)

    # Base64 encode string
    id = b64encode(
        s=username.encode()
    )

    # Store session id
    store = client.set(id, username)

    if not store:
        raise RuntimeError(
            "Unable to store key value pair"
        )
        pass

    return id


def verify_session(id):
    """

    :param id:
    :return:
    """

    # Init redis client
    client = Redis(connection_pool=pool)

    # GET KEY
    session = client.get(id)

    if not session:
        return False

    return session


@app.route("/", methods=["GET"])
def index():
    """

    :return:
    """

    # Map headers
    headers = request.headers

    # Get cookie
    cookie = headers.get("Cookie")

    # Extract value from cookie
    if cookie:
        session_id = cookie.split("=")[-1]
        authenticate = verify_session(session_id)
    else:
        authenticate = None

    # Redirect if not authenticated
    if not authenticate:
        return redirect("/login")

    # Render template
    return render_template("index.html.j2", user=authenticate.decode())


@app.route("/login", methods=["GET", "POST"])
def login():
    """

    :return:
    """

    ## GET METHOD
    if request.method == "GET":
        return render_template("login.html.j2")

    ## POST METHOD

    # Form data credentials
    username = request.form["username"]
    password = request.form["password"]

    # Expected credentials
    # (Hardcoding is fun)
    hardcoded_username = "superuser"
    hardcoded_password = "superpassword"

    # Redirect if username is incorrect
    if username != hardcoded_username:
        return redirect('/login')

    # Redirect if password is incorrect
    if password != hardcoded_password:
        return redirect('/login')

    # Store session and create session id
    session_id = generate_session(username)

    # Create response
    response = make_response(redirect('/'))

    # Set cookie (session id)
    response.set_cookie('session_id', session_id)

    # Return response
    return response


if __name__ == "__main__":
    app.run()