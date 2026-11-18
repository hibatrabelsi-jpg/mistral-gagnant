import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
connection = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM air_quality;")
print(cursor.fetchone())

connection.close()