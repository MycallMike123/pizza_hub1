from sqlalchemy import create_engine, text

engine = create_engine("mysql+pymysql://sql3711398:mxg4gcIUSJ@sql3.freesqldatabase.com/sql3711398?charset=utf8mb4")


def load_restaurants_from_db():
  with engine.connect() as conn:
    result = conn.execute(text("select * from restaurants"))
    restaurants = []
    for row in result.all():
      restaurants.append(dict(row))
    return restaurants

def load_restaurant_from_db(id):
  with engine.connect() as conn:
    result = conn.execute(
      text("SELECT * FROM restaurants WHERE id = :val"), val = id
    )

    rows = result.all()
    if len(rows) == 0:
      return None
    else:
      return dict(rows[0])