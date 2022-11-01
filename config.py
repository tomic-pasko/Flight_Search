import os

# postgres database uri
username = "postgres"
password = os.environ['DB_PASS']
dbname = "postgres"

class Config:
    DEBUG = True
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{username}:{password}@localhost:5432/{dbname}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False



