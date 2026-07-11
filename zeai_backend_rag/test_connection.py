import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

connection = pymysql.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
)

print("✅ Connected to MySQL successfully!")

with connection.cursor() as cursor:
    cursor.execute("SELECT question, answer FROM faqs")
    rows = cursor.fetchall()
    print(f"\nFound {len(rows)} FAQs:")
    for question, answer in rows:
        print(f"- {question}")

connection.close()