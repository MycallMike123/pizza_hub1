PizzaHub
PizzaHub is a streamlined platform designed for efficient pizza ordering. With a user-friendly interface, PizzaHub allows users to browse, filter, and order from a variety of pizza restaurants quickly and easily.


Introduction
Welcome to PizzaHub! This project is designed to make ordering pizza easier by allowing users to filter restaurants by location, cuisine, price, and rating. The project leverages Python, Flask, and MySQL to provide a robust backend and a responsive frontend.

Deployed Site: PizzaHub Deployed Application
Final Project Blog Article: Read the blog post on LinkedIn
Author LinkedIn: https://www.linkedin.com/posts/michael-michire-7574a9179_pizzahub-project-summary-introduction-i-activity-7205805909502046208-KgxD?utm_source=share&utm_medium=member_desktop
Installation
To get started with PizzaHub locally, follow these steps:

Clone the repository:

bash
Copy code
git clone https://github.com/mycall123/pizza_hub1.git
cd pizzahub
Set up the virtual environment:

bash
Copy code
python3 -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Configure the database:

Make sure you have MySQL installed and running on your local machine. Create a new database and update the connection details in database.py:

python
Copy code
engine = create_engine("mysql+pymysql://username:password@localhost/database_name?charset=utf8mb4")
Run the application:

bash
Copy code
flask run
Open your browser:

Go to http://127.0.0.1:5000 to see PizzaHub in action.

Usage
Homepage: Browse the list of available pizza restaurants.
Restaurant Page: View details of a specific restaurant, including location, cuisine, price, and rating.
Order Button: Initiate the ordering process directly from the list of restaurants.
Contributing
Contributions are welcome! Please follow these steps to contribute:

Fork the repository.
Create a new branch: git checkout -b feature-branch.
Make your changes and commit them: git commit -m 'Add some feature'.
Push to the branch: git push origin feature-branch.
Submit a pull request.

Related Projects
Awesome Pizza Ordering Systems
Pizza Ordering App
