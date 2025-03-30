import mysql.connector
import threading
import time

mysql_conn = mysql.connector.connect(
    host="localhost",
    user="mysql",
    password="mysql",
    database="record_label"
)
mysql_conn.autocommit = False  # Disable autocommit to manually control transactions
# print("Connected to database!")

def dirty_read():
    """ Simulates Dirty Read """
    cursor = mysql_conn.cursor()

    # SET TRANSACTION ISOLATION LEVEL before starting the transaction
    cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;")
    cursor.execute("START TRANSACTION;")

    print("\n[Session 1] Modifying country for Artist 1 without commit...")
    cursor.execute("UPDATE Artists SET country = 'United States of America' WHERE artistid = 1;")

    def read_dirty():
        time.sleep(1)
        cursor2 = mysql_conn.cursor()

        # Do NOT set the isolation level again, as it was already set at the beginning
        cursor2.execute("START TRANSACTION;")

        cursor2.execute("SELECT country FROM Artists WHERE artistid = 1;")
        print("[Session 2] Read Dirty Read:", cursor2.fetchone())
        cursor2.close()

    t = threading.Thread(target=read_dirty)
    t.start()

    time.sleep(2)
    print("[Session 1] Performing ROLLBACK...")
    mysql_conn.rollback()
    cursor.close()

def unrepeatable_read():
    """ Simulates Unrepeatable Read """
    cursor = mysql_conn.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED;")

    print("\n[Session 1] Initial read...")
    cursor.execute("SELECT releasedate FROM Albums WHERE title = 'Mayhem';")
    initial_price = cursor.fetchone()
    print("[Session 1] Initial date:", initial_price)

    def update_price():
        time.sleep(1)
        cursor2 = mysql_conn.cursor()
        cursor2.execute("UPDATE Albums SET releasedate = '2025-07-03' WHERE title = 'Mayhem';")
        mysql_conn.commit()
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
    mysql_conn.commit()

def phantom_read():
    """ Simulates Phantom Read with locking """
    cursor = mysql_conn.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;")

    print("\n[Session 1] Initial read (with LOCKING)...")
    cursor.execute("SELECT COUNT(*) FROM ArtistGenres WHERE artistid = 1 FOR UPDATE;")
    initial_count = cursor.fetchone()
    print("[Session 1] Initial number of musical genres:", initial_count)

    def insert_new_purchase():
        time.sleep(2)
        cursor2 = mysql_conn.cursor()
        cursor2.execute("INSERT INTO ArtistGenres (artistid, genreid) VALUES (1, 6);")
        mysql_conn.commit()
        print("[Session 2] Added a new row to ArtistGenres.")
        cursor2.close()

    t = threading.Thread(target=insert_new_purchase)
    t.start()

    time.sleep(3)

    print("[Session 1] Read after modification...")
    cursor.execute("SELECT COUNT(*) FROM ArtistGenres WHERE artistid = 1 FOR UPDATE;")
    new_count = cursor.fetchone()
    print("[Session 1] Final number of musical genres:", new_count)

    cursor.close()
    mysql_conn.commit()

def lost_update():
    """ Simulates Lost Update """
    cursor = mysql_conn.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED;")

    print("\n[Session 1] Initial read...")
    cursor.execute("SELECT title FROM Tracks WHERE trackid = 1;")
    initial_price = cursor.fetchone()
    print("[Session 1] Initial title:", initial_price)

    def update_price():
        time.sleep(1)
        cursor2 = mysql_conn.cursor()
        cursor2.execute("UPDATE Tracks SET title = 'Abracadabra' WHERE trackid = 1;")
        mysql_conn.commit()
        print("[Session 2] Updated the title to 'Abracadabra'")
        cursor2.close()

    t = threading.Thread(target=update_price)
    t.start()

    time.sleep(2)

    print("[Session 1] Updating to 'Disease'")
    cursor.execute("UPDATE Tracks SET title = 'Disease' WHERE trackid = 1;")
    mysql_conn.commit()

    print("[Session 1] Final title:", initial_price)

    cursor.close()

def uncommitted_dependency():
    """ Simulates Uncommitted Dependency """
    cursor = mysql_conn.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED;")

    print("\n[Session 1] Insert without commit...")
    cursor.execute("INSERT INTO ArtistGenres (artistid, genreid) VALUES (1, 7);")

    def read_uncommitted():
        time.sleep(1)
        cursor2 = mysql_conn.cursor()
        cursor2.execute("SELECT * FROM ArtistGenres WHERE artistid = 1;")
        print("[Session 2] Read musical genres:", cursor2.fetchall())
        cursor2.close()

    t = threading.Thread(target=read_uncommitted)
    t.start()

    time.sleep(2)
    print("[Session 1] Performing ROLLBACK...")
    mysql_conn.rollback()

    cursor.close()

# Running tests in MySQL
print("\n=== Test Dirty Read ===")
dirty_read()
print("\n=== Test Unrepeatable Read ===")
unrepeatable_read()
print("\n=== Test Phantom Read ===")
phantom_read()
print("\n=== Test Lost Update ===")
lost_update()
print("\n=== Test Uncommitted Dependency ===")
uncommitted_dependency()