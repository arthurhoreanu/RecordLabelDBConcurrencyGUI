import psycopg2
import threading
import time

pg_conn = psycopg2.connect(
    dbname="record_label",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
pg_conn.autocommit = False  # Disable autocommit for manual transaction control

# PostgreSQL does NOT allow Dirty Read, so this test is not necessary!

def unrepeatable_read():
    """ Simulates Unrepeatable Read """
    cursor = pg_conn.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED;")

    print("\n[Session 1] Initial read...")
    cursor.execute("SELECT releasedate FROM Albums WHERE title = 'Mayhem';")
    initial_price = cursor.fetchone()
    print("[Session 1] Initial date:", initial_price)

    def update_price():
        time.sleep(1)
        cursor2 = pg_conn.cursor()
        cursor2.execute("UPDATE Albums SET releasedate = '2025-07-03' WHERE title = 'Mayhem';")
        pg_conn.commit()
        print("[Session 2] Updated the date to 2025/7/3")
        cursor2.close()

    t = threading.Thread(target=update_price)
    t.start()

    time.sleep(2)

    print("[Session 1] Read after modification...")
    cursor.execute("SELECT releasedate FROM Albums WHERE title = 'Mayhem';")
    new_date = cursor.fetchone()
    print("[Session 1] Date after modification:", new_date)

    cursor.close()
    pg_conn.commit()

def phantom_read():
    """ Simulates Phantom Read with locking """
    cursor = pg_conn.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;")

    print("\n[Session 1] Initial read (with LOCKING)...")

    cursor.execute("SELECT * FROM ArtistGenres WHERE artistid = 1 FOR UPDATE;")
    initial_rows = cursor.fetchall()
    print("[Session 1] Initial number of purchases:", len(initial_rows))

    def insert_new_purchase():
        time.sleep(2)
        cursor2 = pg_conn.cursor()

        cursor2.execute("INSERT INTO ArtistGenres (artistid, genreid) VALUES (1, 6);")
        pg_conn.commit()
        print("[Session 2] Added a new row to purchases.")
        cursor2.close()

    t = threading.Thread(target=insert_new_purchase)
    t.start()

    time.sleep(3)

    print("[Session 1] Read after modification...")
    cursor.execute("SELECT * FROM ArtistGenres WHERE artistid = 1;")
    new_rows = cursor.fetchall()
    print("[Session 1] Final number of purchases:", len(new_rows))

    cursor.close()
    pg_conn.commit()

def lost_update():
    """ Simulates Lost Update """
    cursor = pg_conn.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED;")

    print("\n[Session 1] Initial read...")
    cursor.execute("SELECT title FROM Tracks WHERE trackid = 1;")
    initial_title = cursor.fetchone()
    print("[Session 1] Initial title:", initial_title)

    def update_title():
        time.sleep(1)
        cursor2 = pg_conn.cursor()
        cursor2.execute("UPDATE Tracks SET title = 'Abracadabra' WHERE trackid = 1;")
        pg_conn.commit()
        print("[Session 2] Updated the title to 'Abracadabra'")
        cursor2.close()

    t = threading.Thread(target=update_title)
    t.start()

    time.sleep(2)

    print("[Session 1] Updating to 'Disease'")
    cursor.execute("UPDATE Tracks SET title = 'Disease' WHERE trackid = 1;")
    pg_conn.commit()

    print("[Session 1] Final title:", initial_title)

    cursor.close()

def uncommitted_dependency():
    """ Simulates Uncommitted Dependency """
    cursor = pg_conn.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED;")

    print("\n[Session 1] Insert without commit...")

    cursor.execute("INSERT INTO ArtistGenres (artistid, genreid) VALUES (1, 7);")

    def read_uncommitted():
        time.sleep(1)
        cursor2 = pg_conn.cursor()
        cursor2.execute("SELECT * FROM ArtistGenres WHERE artistid = 1;")
        print("[Session 2] Read musical genres:", cursor2.fetchall())
        cursor2.close()

    t = threading.Thread(target=read_uncommitted)
    t.start()

    time.sleep(2)
    print("[Session 1] Performing ROLLBACK...")
    pg_conn.rollback()

    cursor.close()

# Running tests in PostgreSQL
print("\n=== Test Unrepeatable Read ===")
unrepeatable_read()
print("\n=== Test Phantom Read ===")
phantom_read()
print("\n=== Test Lost Update ===")
lost_update()
print("\n=== Test Uncommitted Dependency ===")
uncommitted_dependency()