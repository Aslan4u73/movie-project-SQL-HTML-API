from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, OperationalError

# Database path
DB_URL = "sqlite:///data/movies.db"
engine = create_engine(DB_URL)


def create_table():
    """Create the movies table if it does not exist."""
    with engine.connect() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                year INTEGER NOT NULL,
                rating REAL NOT NULL,
                poster_url TEXT
            )
        """))
        connection.commit()


def list_movies():
    """Retrieve all movies from the database."""
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT title, year, rating, poster_url FROM movies")
            )
            movies = result.fetchall()
            return {
                row[0]: {
                    "year": row[1],
                    "rating": row[2],
                    "poster_url": row[3]
                }
                for row in movies
            }
    except OperationalError as e:
        print(f"Database error: {e}")
        return {}


def add_movie(title, year, rating, poster_url=""):
    """Add a new movie to the database."""
    try:
        with engine.connect() as connection:
            connection.execute(
                text(
                    "INSERT INTO movies (title, year, rating, poster_url) "
                    "VALUES (:title, :year, :rating, :poster_url)"
                ),
                {
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "poster_url": poster_url
                }
            )
            connection.commit()
            print(f"Movie '{title}' added successfully.")
    except IntegrityError:
        print(f"Movie '{title}' already exists.")
    except OperationalError as e:
        print(f"Database error: {e}")


def delete_movie(title):
    """Delete a movie from the database."""
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("DELETE FROM movies WHERE title = :title"),
                {"title": title}
            )
            connection.commit()
            if result.rowcount > 0:
                print(f"Movie '{title}' deleted successfully.")
            else:
                print(f"Movie '{title}' not found.")
    except OperationalError as e:
        print(f"Database error: {e}")


def update_movie(title, rating):
    """Update a movie's rating in the database."""
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text(
                    "UPDATE movies SET rating = :rating "
                    "WHERE title = :title"
                ),
                {"title": title, "rating": rating}
            )
            connection.commit()
            if result.rowcount > 0:
                print(f"Movie '{title}' updated successfully.")
            else:
                print(f"Movie '{title}' not found.")
    except OperationalError as e:
        print(f"Database error: {e}")


# Create table when module is loaded
create_table()
