from flask import Flask, render_template, jsonify
from database import load_restaurants_from_db, load_restaurant_from_db


app = Flask(__name__)


@app.route("/")
def hello_world():
  restaurants = load_restaurants_from_db()
  return render_template("home.html", restaurants = restaurants)

@app.route("/api/restaurants")
def list_restaurants():
  restaurants = load_restaurants_from_db()
  return jsonify(restaurants)

@app.route("/restaurant/<id>")
def show_restaurant(id):
  restaurant = load_restaurant_from_db(id)
  if not restaurant:
    return "Not Found", 404
  return render_template('restaurantpage.html', restaurant = restaurant)

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)