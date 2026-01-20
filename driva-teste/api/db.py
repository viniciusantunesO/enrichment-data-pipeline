import psycopg2

def get_connection():
    return psycopg2.connect(
        host="postgres",
        port=5432,
        database="driva_db",
        user="driva",
        password="driva"
    )
