# Movies App - SQL, API and HTML

A command-line movie database application.

## Features
- Add, delete, update and list movies
- Fetch movie data from OMDb API
- Generate a static HTML website
- SQLite database with SQLAlchemy

## Setup
```
pip install -r requirements.txt
```

Create a `.env` file with your API key:
```
OMDB_API_KEY=your_key_here
```

## Run
```
python movies.py
```

## File Structure
```
movies.py               - Main application
movie_storage_sql.py    - Database operations (SQLAlchemy)
requirements.txt        - Dependencies
.env                    - API key (not in git)
_static/                - Website template and styles
  index_template.html
  style.css
data/                   - SQLite database (auto-created)
```
