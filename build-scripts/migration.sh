cd ../api/app
# alemibc init alembic
alembic revision --autogenerate -m "$1"
alembic upgrade head