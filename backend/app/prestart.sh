#! /usr/bin/env bash
echo "Running inside /app/prestart.sh, you could add migrations to this file, e.g.:"
# Let the DB start
python /app/app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python /app/app/initial_data.py
