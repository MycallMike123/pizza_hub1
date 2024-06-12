from flask import Flask, render_template, jsonify
from database import load_restaurants_from_db, load_restaurant_from_db

# Initialize the Flask application
app = Flask(__name__)

# Define the route for the homepage
@app.route("/")
def hello_world():
    # Load restaurant data from the database
    restaurants = load_restaurants_from_db()
    # Render the home.html template with the loaded restaurant data
    return render_template("home.html", restaurants=restaurants)

# Define the route for the API endpoint to list all restaurants
@app.route("/api/restaurants")
def list_restaurants():
    # Load restaurant data from the database
    restaurants = load_restaurants_from_db()
    # Return the restaurant data as JSON
    return jsonify(restaurants)

# Define the route for displaying a specific restaurant's details
@app.route("/restaurant/<id>")
def show_restaurant(id):
    # Load specific restaurant data from the database using the provided ID
    restaurant = load_restaurant_from_db(id)
    # If the restaurant is not found, return a 404 error
    if not restaurant:
        return "Not Found", 404
    # Render the restaurantpage.html template with the specific restaurant data
    return render_template('restaurantpage.html', restaurant=restaurant)

# Run the Flask application
if __name__ == "__main__":
    # Set the host to '0.0.0.0' to make the server publicly available, and enable debug mode
    app.run(host='0.0.0.0', debug=True)
