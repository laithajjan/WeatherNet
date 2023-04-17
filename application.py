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

        if 'location' not in data:
            print(f"No weather data found for the city: {city_name}")
            return None

        location = data["location"]
        current = data["current"]

        weather_info = {
            "query": data["request"]["query"],
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

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        city = request.form["city"]
        url = f"http://api.weatherstack.com/current?access_key=7b65f2844eba75ec0d2fd0944a7a66c1&query={city}"
        response = requests.get(url)
        data = response.json()

        weather_data = {
            "query": data["request"]["query"],
            "lat": data["location"]["lat"],
            "lon": data["location"]["lon"],
            "localtime": data["location"]["localtime"],
            "temperature": data["current"]["temperature"],
            "wind_speed": data["current"]["wind_speed"],
            "humidity": data["current"]["humidity"],
            "precip": data["current"]["precip"],
            "weather_icons": data["current"]["weather_icons"],
            "weather_descriptions": data["current"]["weather_descriptions"],
            "feelslike": data["current"]["feelslike"]
        }

        return render_template("search.html", weather_data=weather_data)
    else:
        return render_template("search.html")


@app.route("/details/<city>", methods=["GET"])
def details(city):
    weather_data = fetch_weather_data(city)
    if weather_data:
        return render_template("details.html", weather_data=weather_data, city=city)
    else:
        return render_template("error.html", message="Error fetching weather data.")
