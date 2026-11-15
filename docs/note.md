export FINFLOW_DATABASE_URL='postgresql+psycopg://finflow:finflow_local_password@localhost:5432/finflow'
alembic revision --autogenerate -m "add ingestion batches and integrity constraints"
alembic upgrade head
alembic current
docker compose exec postgres psql -U finflow -d finflow -c "\d+ transactions"

docker compose exec postgres psql -U finflow -d finflow -c "SELECT conname FROM pg_constraint WHERE conrelid = 'ingestion_batches'::regclass ORDER BY conname;"





 