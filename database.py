from sqlalchemy import create_engine, text

# Create a connection to the MySQL database using SQLAlchemy and pymysql
engine = create_engine("mysql+pymysql://sql3711398:mxg4gcIUSJ@sql3.freesqldatabase.com/sql3711398?charset=utf8mb4")

def load_restaurants_from_db():
  """Load all restaurants from the database and return as a list of dictionaries."""
  with engine.connect() as conn:
    # Execute the SQL query to select all rows from the 'restaurants' table
    result = conn.execute(text("SELECT * FROM restaurants"))
    
    # Initialize an empty list to store restaurant data
    restaurants = []
    
    # Iterate over the result set and convert each row to a dictionary
    for row in result.all():
      restaurants.append(dict(row))
    
    # Return the list of restaurant dictionaries
    return restaurants

def load_restaurant_from_db(id):
  """Load a specific restaurant from the database by its ID."""
  with engine.connect() as conn:
    # Execute the SQL query to select a row from the 'restaurants' table where the ID matches
    result = conn.execute(
      text("SELECT * FROM restaurants WHERE id = :val"), val = id
    )
    
    # Fetch all rows from the result set
    rows = result.all()
    
    # If no rows are found, return None
    if len(rows) == 0:
      return None
    else:
      # Convert the first row to a dictionary and return it
      return dict(rows[0])
