from database import get_db_connection

def init_db():
    with get_db_connection() as db:

        # ================= USERS TABLE =================
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)

        # ================= ARTISTS TABLE =================
        db.execute("""
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                bio TEXT,
                mobile TEXT,
                email TEXT,
                photo TEXT
            )
        """)

        # ================= ARTWORKS TABLE =================
        db.execute("""
            CREATE TABLE IF NOT EXISTS artworks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist_id INTEGER,
                price INTEGER,
                description TEXT,
                image TEXT,
                FOREIGN KEY (artist_id) REFERENCES artists(id)
            )
        """)

        # ================= REQUESTS TABLE =================
        db.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist_username TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)

        # ================= PAYMENTS TABLE =================
        db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                artwork_id INTEGER,
                amount INTEGER,
                payment_method TEXT,
                status TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ================= DEFAULT ADMIN =================
        admin = db.execute(
            "SELECT * FROM users WHERE username = ?",
            ("admin",)
        ).fetchone()

        if not admin:
            db.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, ("admin", "admin", "admin"))

        db.commit()


if __name__ == "__main__":
    init_db()
    print("Database Initialized Successfully!")
