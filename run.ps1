$env:DATABASE_URL = 'postgresql+psycopg://licitra_user:licitra_pass@localhost:5432/licitra'
python -m uvicorn backend.app.main:app --reload
