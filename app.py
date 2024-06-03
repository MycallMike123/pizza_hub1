from flask import Flask, render_template, jsonify
from database import engine
from sqlalchemy import text


app = Flask(__name__)


def load_restaurants_from_db():
  with engine.connect() as conn:
    result = conn.execute(text("select * from restaurants"))
    restaurants = []
    for row in result.all():
      restaurants.append(dict(row))
    return restaurants

@app.route("/")
def hello_world():
  restaurants = load_restaurants_from_db()
  return render_template("home.html", restaurants = restaurants)

@app.route("/api/restaurants")
def list_restaurants():
  return jsonify(RESTAURANTS)


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)