# FastAPI Project with Alembic

This project is a FastAPI application which have features of chat application including one-to-one chat and group chat

## Prerequisites

Before you start, make sure you have the following installed:

- **Python 3.8+**
- **pip** (Python package manager)
- **PostgreSQL** (or any other supported database)
- **virtualenv** (optional, but recommended for virtual environments)

### Dependencies

This project uses the following key dependencies:

- [FastAPI](https://fastapi.tiangolo.com/) — The web framework for building APIs.
- [SQLAlchemy](https://www.sqlalchemy.org/) — The ORM used for interacting with the database.
- [Alembic](https://alembic.sqlalchemy.org/) — A database migration tool for SQLAlchemy.
- [asyncpg](https://github.com/MagicStack/asyncpg) — PostgreSQL database driver (for async operations).
- [pydantic](https://pydantic-docs.helpmanual.io/) — Data validation and settings management.
- [uvicorn](https://www.uvicorn.org/) — ASGI server for serving the FastAPI app.

You can install all dependencies in a virtual environment using the following command:

pip install -r requirements.txt

## Project Setup
### 1. Clone the repository:
```

git clone https://github.com/komalrajput0801/whatsapp_fastapi_clone.git
cd whatsapp_clone

```

### 2. Create and activate a virtual environment:
```

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```

### 3. Install dependencies using pip:
```

pip install -r requirements.txt

```

OR

### 3. Install dependencies using poetry
```
pip install poetry
poetry install
```

### 4. Configure the environment variables for your database. Create a .env file in the root directory and add the following:
```

DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

```

### 5. Run migrations
```

alembic upgrade head

```

## Running the Application
To run the FastAPI application, use Uvicorn:
```

uvicorn app.main:app --reload

```

## API documentation
```
http://localhost:8000/docs
```