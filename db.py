import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('newspaper_agency.db')
cursor = conn.cursor()

# Check the alembic_version table
cursor.execute("SELECT * FROM alembic_version")
version = cursor.fetchone()

print(f"Alembic version: {version}")

# Close the connection
conn.close()
