import os
import requests
from flask import Flask, session, render_template, request
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = 'mysecretkey'

database_url = "postgresql://postgres:laith123@localhost/postgres"
engine = create_engine(database_url)
db = scoped_session(sessionmaker(bind=engine))

def fetch_weather_data(city_name):
    try:
        response = requests.get(f"http://api.weatherstack.com/current?access_key=7b65f2844eba75ec0d2fd0944a7a66c1&query={city_name}")
        print("request sent")
        data = response.json()
        location = data["location"]
        current = data["current"]

        weather_info = {
            "lat": location["lat"],
            "lon": location["lon"],
            "localtime": location["localtime"],
            "temperature": current["temperature"],
            "wind_speed": current["wind_speed"],
            "humidity": current["humidity"],
            "precip": current["precip"],
            "weather_icons": current["weather_icons"],
            "weather_descriptions": current["weather_descriptions"],
            "feelslike": current["feelslike"],
            "uv_index": current["uv_index"]
        }
        print(weather_info)
        return weather_info
    except Exception as error:
        print(f"Error fetching weather data: {error}")
        return None

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        session['username'] = username
        if not username or not password:
            return render_template("error.html", message="Please fill out the form.")
        users = db.execute(text("SELECT * from users where username= :username"), {"username": username}).fetchall()
        db.commit()
        return render_template("login.html", success=1, users=users)
    return render_template("login.html", success=0)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return render_template("error.html", message="Please fill out the form.")
        db.execute(text("INSERT INTO users (username, password) VALUES (:username, :password)"),
                   {"username": username, "password": password})
        db.commit()
        return render_template("register.html", success=1)
    return render_template("register.html", success=0)

@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        city_name = request.form["city"]
        print("before")
        weather_data = fetch_weather_data(city_name)
        print("after")
        if weather_data is not None:
            # Pass the weather data to your template for rendering
            return render_template("search.html", weather_data=weather_data)
        else:
            # Redirect to an error page or display an error message
            return render_template("error.html", message="An error occurred while fetching weather data.")

    return render_template("search.html")
