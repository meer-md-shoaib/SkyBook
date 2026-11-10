"""SkyBook entry point.

Run the development server with::

    python run.py
"""
from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402  (after env vars are loaded)

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=app.config.get("DEBUG", False))
