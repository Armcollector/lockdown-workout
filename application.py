"""
This script runs the app application using a development server.
"""

import os

from app import app, db, views
from app.models import Pushupchallenge_user


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "user": Pushupchallenge_user}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ.get("PORT"))
