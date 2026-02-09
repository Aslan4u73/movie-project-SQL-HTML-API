import random
import os
import requests
from dotenv import load_dotenv
import movie_storage_sql as storage


# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OMDB_API_KEY", "")
API_URL = "http://www.omdbapi.com/"

# Color theme
THEME = "\033[0;92;40m"
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"

# Validation limits
MIN_YEAR = 1888
MAX_YEAR = 2026
MIN_RATING = 0
MAX_RATING = 10


def clear():
    """Clear the terminal screen."""
    print("\033[H\033[2J", end="")


def format_movie_line(title, info, width=45):
    """Build a formatted line for movie display."""
    rating = info.get("rating", 0.0)
    year = info.get("year", "")
    label = f" {title} ({year})"
    value = f" {rating}"
    dots = width - len(label) - len(value)
    if dots < 3:
        dots = 3
    return f"{label} {'.' * dots}{value}"


def fetch_movie_data(title):
    """Fetch movie data from OMDb API by title."""
    if not API_KEY:
        print(f"{RED}  API key not found. Check your .env file.{RESET}")
        return None
    try:
        response = requests.get(
            API_URL,
            params={"apikey": API_KEY, "t": title},
            timeout=10
        )
        data = response.json()
        if data.get("Response") == "True":
            return {
                "title": data.get("Title", title),
                "year": int(data.get("Year", "0")[:4]),
                "rating": float(data.get("imdbRating", "0")),
                "poster_url": data.get("Poster", "")
            }
        else:
            print(f"{RED}  Movie not found: {data.get('Error')}{RESET}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"{RED}  API error: {e}{RESET}")
        return None


def get_valid_rating():
    """Ask for a rating between 0 and 10."""
    while True:
        try:
            rating = float(input("  Enter rating (0-10): "))
            if MIN_RATING <= rating <= MAX_RATING:
                return rating
            print(f"{RED}  Rating must be between 0 and 10.{RESET}")
        except ValueError:
            print(f"{RED}  Please enter a valid number.{RESET}")


def get_valid_year():
    """Ask for a valid year."""
    while True:
        try:
            year = int(input("  Enter year: "))
            if MIN_YEAR <= year <= MAX_YEAR:
                return year
            print(f"{RED}  Year must be between "
                  f"{MIN_YEAR} and {MAX_YEAR}.{RESET}")
        except ValueError:
            print(f"{RED}  Please enter a valid year.{RESET}")


def list_movies():
    """Display all movies from the database."""
    movies = storage.list_movies()
    if not movies:
        print(f"\n{RED}  No movies in database yet.{RESET}")
        return

    print(f"\n{THEME}  {len(movies)} movies in total:{RESET}\n")
    for title, info in movies.items():
        line = format_movie_line(title, info)
        print(f"{THEME}{line}{RESET}")


def add_movies():
    """Add a movie - fetches data from OMDb API."""
    print(f"\n{THEME}  ADD MOVIE{RESET}")
    title = input("\n  Enter movie name: ").strip()
    if not title:
        print(f"{RED}  Title cannot be empty.{RESET}")
        return

    print(f"\n  Searching OMDb for '{title}'...")
    data = fetch_movie_data(title)

    if data:
        print(f"\n  Found: {data['title']} ({data['year']}) "
              f"- Rating: {data['rating']}")
        storage.add_movie(
            data["title"],
            data["year"],
            data["rating"],
            data.get("poster_url", "")
        )
    else:
        print(f"\n{RED}  Could not fetch from API. "
              f"Enter manually:{RESET}")
        year = get_valid_year()
        rating = get_valid_rating()
        storage.add_movie(title, year, rating)


def del_movies():
    """Delete a movie from the database."""
    print(f"\n{THEME}  DELETE MOVIE{RESET}")
    title = input("\n  Enter movie name to delete: ").strip()
    if not title:
        print(f"{RED}  Title cannot be empty.{RESET}")
        return
    storage.delete_movie(title)


def update_movies():
    """Update a movie rating in the database."""
    print(f"\n{THEME}  UPDATE MOVIE{RESET}")
    title = input("\n  Enter movie name: ").strip()
    if not title:
        print(f"{RED}  Title cannot be empty.{RESET}")
        return
    rating = get_valid_rating()
    storage.update_movie(title, rating)


def stats_movies():
    """Show movie statistics."""
    movies = storage.list_movies()
    if not movies:
        print(f"\n{RED}  No movies to show stats for.{RESET}")
        return

    ratings = [info["rating"] for info in movies.values()]
    best = max(movies.items(), key=lambda x: x[1]["rating"])
    worst = min(movies.items(), key=lambda x: x[1]["rating"])
    avg = sum(ratings) / len(ratings)

    print(f"\n{THEME}  STATISTICS{RESET}")
    print(f"  Average rating: {avg:.1f}")
    print(f"  Best movie: {best[0]} ({best[1]['rating']})")
    print(f"  Worst movie: {worst[0]} ({worst[1]['rating']})")


def random_movie():
    """Pick a random movie from the database."""
    movies = storage.list_movies()
    if not movies:
        print(f"\n{RED}  No movies available.{RESET}")
        return

    title = random.choice(list(movies.keys()))
    info = movies[title]
    print(f"\n{GREEN}  Random pick: {title} ({info['year']}) "
          f"- Rating: {info['rating']}{RESET}")


def search_movie():
    """Search for a movie by partial title."""
    query = input("\n  Enter search term: ").strip().lower()
    if not query:
        return

    movies = storage.list_movies()
    found = False
    for title, info in movies.items():
        if query in title.lower():
            line = format_movie_line(title, info)
            print(f"{GREEN}{line}{RESET}")
            found = True

    if not found:
        print(f"{RED}  No movies found matching '{query}'.{RESET}")


def movies_sorted_by_rating():
    """Display movies sorted by rating (highest first)."""
    movies = storage.list_movies()
    if not movies:
        print(f"\n{RED}  No movies to sort.{RESET}")
        return

    sorted_movies = sorted(
        movies.items(),
        key=lambda x: x[1]["rating"],
        reverse=True
    )

    print(f"\n{THEME}  MOVIES SORTED BY RATING:{RESET}\n")
    for title, info in sorted_movies:
        line = format_movie_line(title, info)
        print(f"{THEME}{line}{RESET}")


def generate_website():
    """Generate a static HTML website from the movie database."""
    movies = storage.list_movies()

    template_path = os.path.join("_static", "index_template.html")
    try:
        with open(template_path, "r") as f:
            template = f.read()
    except FileNotFoundError:
        print(f"{RED}  Template not found: {template_path}{RESET}")
        return

    movie_grid = ""
    for title, info in movies.items():
        poster = info.get("poster_url", "")
        year = info.get("year", "")
        rating = info.get("rating", 0)

        movie_grid += "        <li>\n"
        movie_grid += "            <div class='movie'>\n"
        if poster and poster != "N/A":
            movie_grid += (
                f"                <img class='movie-poster' "
                f"src='{poster}' alt='{title}'/>\n"
            )
        movie_grid += (
            f"                <div class='movie-title'>"
            f"{title}</div>\n"
        )
        movie_grid += (
            f"                <div class='movie-year'>"
            f"{year}</div>\n"
        )
        movie_grid += (
            f"                <div class='movie-rating'>"
            f"Rating: {rating}</div>\n"
        )
        movie_grid += "            </div>\n"
        movie_grid += "        </li>\n"

    output = template.replace("__TEMPLATE_TITLE__", "My Movie App")
    output = output.replace("__TEMPLATE_MOVIE_GRID__", movie_grid)

    output_path = os.path.join("_static", "index.html")
    with open(output_path, "w") as f:
        f.write(output)

    print(f"\n{GREEN}  Website was generated successfully.{RESET}")
    print(f"  Open {output_path} to view it.")


def main():
    """Main menu loop for the movie app."""
    os.makedirs("data", exist_ok=True)

    print(f"\n{THEME}")
    print("  ==============================")
    print("   RETRO MOVIE DATABASE v2.0")
    print("  ==============================")
    print(f"{RESET}")

    while True:
        print(f"\n{THEME}  Menu:{RESET}")
        print("  0. Exit")
        print("  1. List movies")
        print("  2. Add movie")
        print("  3. Delete movie")
        print("  4. Update movie")
        print("  5. Stats")
        print("  6. Random movie")
        print("  7. Search movie")
        print("  8. Movies sorted by rating")
        print("  9. Generate website")

        choice = input("\n  Enter choice (0-9): ").strip()

        if choice == "0":
            print(f"\n{GREEN}  Bye! See you next time.{RESET}")
            return
        elif choice == "1":
            list_movies()
        elif choice == "2":
            add_movies()
        elif choice == "3":
            del_movies()
        elif choice == "4":
            update_movies()
        elif choice == "5":
            stats_movies()
        elif choice == "6":
            random_movie()
        elif choice == "7":
            search_movie()
        elif choice == "8":
            movies_sorted_by_rating()
        elif choice == "9":
            generate_website()
        else:
            print(f"{RED}  Invalid choice. Try again.{RESET}")

        input("\n  Press enter to Menu")


if __name__ == "__main__":
    main()
