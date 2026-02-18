from flask import Flask, render_template, request, redirect, session, url_for
from database import get_db_connection
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "secretkey"

# =========================
# UPLOAD CONFIG
# =========================
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# =========================
# INIT DATABASE
# =========================
def init_db():
    with get_db_connection() as db:

        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                bio TEXT,
                mobile TEXT,
                email TEXT,
                photo TEXT
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS artworks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                artist_id INTEGER,
                price INTEGER,
                description TEXT,
                image TEXT
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist_username TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)

        # 🔥 ADD THIS
        db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                amount INTEGER,
                payment_method TEXT,
                status TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        db.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        art_name TEXT,
        amount INTEGER,
        payment_method TEXT,
        status TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")


        # default admin
        admin = db.execute(
            "SELECT * FROM users WHERE username=?",
            ("admin",)
        ).fetchone()

        if not admin:
            db.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("admin", "admin", "admin")
            )



        db.commit()


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("home.html")

# =========================
# CONTACT
# =========================
@app.route("/contact")
def contact():
    return render_template("contact.html")

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        with get_db_connection() as db:
            user = db.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (request.form["username"], request.form["password"])
            ).fetchone()

        if user:
            session["username"] = user["username"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("admin"))
            elif user["role"] == "artist":
                return redirect(url_for("artist"))
            elif user["role"] == "customer":
                return redirect(url_for("customer"))

        return render_template("login.html", error="Invalid login")

    return render_template("login.html")

# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        with get_db_connection() as db:
            user = db.execute(
                "SELECT 1 FROM users WHERE username=?",
                (request.form["username"],)
            ).fetchone()

            if user:
                return render_template("register.html", error="Username already exists")

            db.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (
                    request.form["username"],
                    request.form["password"],
                    request.form["role"]
                )
            )
            db.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    with get_db_connection() as db:
        return render_template(
            "admin.html",
            requests=db.execute(
                "SELECT * FROM requests WHERE status='pending'"
            ).fetchall(),

            artists=db.execute(
                "SELECT * FROM artists"
            ).fetchall(),

            artworks=db.execute("""
                SELECT artworks.*, artists.name
                FROM artworks
                JOIN artists ON artworks.artist_id = artists.id
            """).fetchall(),

            payments=db.execute(
                "SELECT * FROM payments ORDER BY date DESC"
            ).fetchall()
        )


# =========================
# ADD ARTIST
# =========================
@app.route("/add_artist", methods=["POST"])
def add_artist():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    photo = request.files.get("photo")
    filename = None

    if photo and photo.filename != "":
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    with get_db_connection() as db:
        db.execute("""
            INSERT INTO artists (name, mobile, email, bio, photo)
            VALUES (?, ?, ?, ?, ?)
        """, (
            request.form["name"],
            request.form["mobile"],
            request.form["email"],
            request.form["bio"],
            filename
        ))
        db.commit()

    return redirect(url_for("admin"))

@app.route("/delete_artist/<int:artist_id>")
def delete_artist(artist_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    with get_db_connection() as db:
        db.execute("DELETE FROM artists WHERE id = ?", (artist_id,))
        db.commit()

    return redirect(url_for("admin"))

# =========================
# ADD ARTWORK
# =========================
@app.route("/add-artwork", methods=["POST"])
def add_artwork():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    image = request.files["art_image"]
    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    with get_db_connection() as db:
        db.execute("""
            INSERT INTO artworks (title, artist_id, price, description, image)
            VALUES (?, ?, ?, ?, ?)
        """, (
            request.form["art_title"],
            request.form["artist_id"],
            request.form["price"],
            request.form["description"],
            filename
        ))
        db.commit()

    return redirect(url_for("admin"))
# =========================
# DELETE ARTWORK
# =========================


@app.route('/delete_artwork/<int:art_id>')
def delete_artwork(art_id):
    db = get_db_connection()
    db.execute("DELETE FROM artworks WHERE id = ?", (art_id,))
    db.commit()
    db.close()
    return redirect(url_for('admin'))



# =========================
# ARTIST DASHBOARD
# =========================
@app.route("/artist")
def artist():
    if session.get("role") != "artist":
        return redirect(url_for("login"))

    with get_db_connection() as db:
        artists = db.execute("SELECT * FROM artists").fetchall()

    return render_template("artist.html", artists=artists)

#================
#view
#===============
@app.route("/artwork/<int:art_id>")
def artwork_details(art_id):
    with get_db_connection() as db:
        art = db.execute("""
            SELECT artworks.*, artists.name
            FROM artworks
            JOIN artists ON artworks.artist_id = artists.id
            WHERE artworks.id = ?
        """, (art_id,)).fetchone()

    if not art:
        return "Artwork not found", 404

    return render_template("artwork_details.html", art=art)
# =========================
# PAYMENT
# =========================
@app.route("/payment/<int:art_id>")
def payment(art_id):

    if "username" not in session:
        return redirect(url_for("login"))

    with get_db_connection() as db:
        art = db.execute("""
            SELECT artworks.*, artists.name
            FROM artworks
            JOIN artists ON artworks.artist_id = artists.id
            WHERE artworks.id = ?
        """, (art_id,)).fetchone()

    if not art:
        return "Artwork not found", 404

    return render_template("payment.html", art=art)



#============== 
#pr
#===============
@app.route("/qr_payment", methods=["POST"])
def qr_payment():

    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    art_id = request.form.get("art_id")

    with get_db_connection() as db:

        # 🔥 Get title + price
        art = db.execute(
            "SELECT title, price FROM artworks WHERE id = ?",
            (art_id,)
        ).fetchone()

        if not art:
            return "Artwork not found", 404

        # 🔥 Insert with painting name
        db.execute("""
            INSERT INTO payments (username, art_name, amount, payment_method, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            username,
            art["title"],   # 👈 THIS IS IMPORTANT
            art["price"],
            "QR Code",
            "Success"
        ))

        db.commit()

    return redirect(url_for("customer"))



@app.route("/delete_payment/<int:payment_id>")
def delete_payment(payment_id):

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    with get_db_connection() as db:
        db.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
        db.commit()

    return redirect(url_for("admin"))




# =========================
# CUSTOMER DASHBOARD
# =========================
@app.route("/customer")
def customer():
    if session.get("role") != "customer":
        return redirect(url_for("login"))

    with get_db_connection() as db:
        artworks = db.execute("""
            SELECT artworks.*, artists.name
            FROM artworks
            JOIN artists ON artworks.artist_id = artists.id
        """).fetchall()

    return render_template("customer.html", artworks=artworks)

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# =========================
# RUN
# =========================


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
