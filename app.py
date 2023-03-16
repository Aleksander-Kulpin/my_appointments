from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, admin_required, specialist_required,\
get_day, get_yes_no, set_date, change_format_date, date_for_db, date_before_current

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///myapp.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show information for a client"""
    # Get the current user's ID
    current_user_id = session["user_id"]
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure id of appointment was submitted
        if not request.form.get("id"):
            return apology("must provide a time slot", 400)
        # Create a booking in database - booking
        db.execute("UPDATE appointments SET client_id = ? WHERE id = ?",\
            current_user_id, request.form.get("id"))

    # User reached route via GET (as by clicking a link or via redirect)

    # Get the information about all the available slots
    agg_rows_client = db.execute("SELECT ap.id, date, time,\
        services.name AS service, specialists.firstlast AS specialist,\
        users.username AS client, is_available, client_id FROM appointments AS ap\
        JOIN services ON ap.service_id = services.id\
        JOIN specialists ON ap.specialist_id = specialists.id\
        LEFT JOIN users ON ap.client_id = users.id\
        ORDER BY date, time ASC")
    # Lists for tables
    info_search = []
    info_schedule_client = []
    info_history_client = []
    # Filter data into three categories for three tables
    for row in agg_rows_client:
        if not date_before_current(row['date'], row['time']):
            if row['is_available'] == 1 and row['client_id'] == 0:
                info_search.append(row)
            elif row['client_id'] == current_user_id:
                info_schedule_client.append(row)
        else :
            if row['client_id'] == current_user_id:
                info_history_client.append(row)
    # date formatting
    for row in info_search:
        row['date'] = change_format_date(row['date'])
    for row in info_schedule_client:
        row['date'] = change_format_date(row['date'])
    for row in info_history_client:
        row['date'] = change_format_date(row['date'])

    return render_template("index.html", info_search=info_search,\
         info_schedule_client=info_schedule_client, info_history_client=info_history_client)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ? AND is_deleted IS NULL", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password was repeated correctly
        elif not (request.form.get("password") == request.form.get("confirmation")):
            return apology("passwords are not same", 400)

        # Ensure that length of the new password at least 6 symbols
        if not (len(request.form.get("password")) >= 6):
            return apology("length of the password must be at least 6 symbols", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username has not been created before
        if len(rows) != 0:
            return apology("username already exists", 400)

        # Remember registrant
        name = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", name, hash)

        # Confirm registration
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/change", methods=["GET", "POST"])
@login_required
def change_password():
    """Change current user's password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure old password was submitted
        if not request.form.get("old_password"):
            return apology("must provide username", 400)

        # Ensure old password is correct
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if not check_password_hash(rows[0]["hash"], request.form.get("old_password")):
            return apology("old password is not correct", 400)

        # Ensure new password was submitted
        if not request.form.get("new_password"):
            return apology("must provide a new password", 400)

        # Ensure password was repeated correctly
        if not (request.form.get("new_password") == request.form.get("confirmation")):
            return apology("new passwords are not same", 400)

        # Ensure that length of the new password at least 6 symbols
        if not (len(request.form.get("new_password")) >= 6):
            return apology("length of the cd password must be at least 6 symbols", 400)

        # Remember new password
        hash = generate_password_hash(request.form.get("new_password"))
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, session["user_id"])

        # Confirm registration
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change.html")


@app.route("/specialist")
@login_required
@specialist_required

def specialist():
    """Show information for a specialist"""

    # Get the current user's specialist ID
    rows = db.execute("SELECT id FROM specialists WHERE user_id = ?", session["user_id"])
    current_user_specialist_id = rows[0]["id"]

    # Get the information about all the appointments (available slots + history)
    agg_rows_specialist = db.execute("SELECT date, time,\
        services.name AS service, specialists.firstlast AS specialist,\
        users.username AS client FROM appointments AS ap\
        JOIN services ON ap.service_id = services.id\
        JOIN specialists ON ap.specialist_id = specialists.id\
        LEFT JOIN users ON ap.client_id = users.id\
        WHERE ap.specialist_id = ?\
        ORDER BY date, time ASC", current_user_specialist_id)
    agg_rows_roster = []
    agg_rows_history = []

    for row in agg_rows_specialist:
        if not date_before_current(row['date'], row['time']):
            agg_rows_roster.append(row)
        else:
            agg_rows_history.append(row)

    for row in agg_rows_roster:
        row['date'] = change_format_date(row['date'])

    for row in agg_rows_history:
        row['date'] = change_format_date(row['date'])

    return render_template("specialist.html", info_roster=agg_rows_roster, info_history=agg_rows_history)


@app.route("/admin", methods=["GET", "POST"])
@login_required
@admin_required

def admin():
    """Show information for an admin"""
    # Get the information about all the appointments (available slots + history)
    agg_rows_app = db.execute("SELECT ap.id, date, time, services.name AS service, specialists.firstlast AS specialist,\
        is_available, users.username AS client FROM appointments AS ap\
        JOIN services ON ap.service_id = services.id\
        JOIN specialists ON ap.specialist_id = specialists.id\
        LEFT JOIN users ON ap.client_id = users.id\
        ORDER BY date, time ASC")

    for row in agg_rows_app:
        row['is_available'] = get_yes_no(row['is_available']) #Add yes/no in availability column
        row['before_date'] = date_before_current(row['date'], row['time']) #Add information for booking-by-admin possibility
        row['date'] = change_format_date(row['date']) #Change date format for displaying in the table

    # Get the information about all the templates
    agg_rows_templates = db.execute("SELECT st.id, day, time, services.name AS service,\
        specialists.firstlast AS specialist, is_available\
        FROM schedule_templates AS st, services,  specialists\
        WHERE st.service_id =  services.id\
        AND st.specialist_id =  specialists.id\
        ORDER BY day, time ASC")

    for row in agg_rows_templates:
        row['day'] = get_day(row['day'])                      #Add day of week instead number
        row['is_available'] = get_yes_no(row['is_available']) #Add yes/no in availability column

    # Get info for dropdowns and Tab 3
    list_users = db.execute("SELECT id, username, is_admin, is_specialist FROM users WHERE is_deleted IS NULL")

    for row in list_users:
        row['is_admin'] = get_yes_no(row['is_admin']) #Add yes/no for roles
        row['is_specialist'] = get_yes_no(row['is_specialist']) #Add yes/no for roles

    return render_template("admin.html", information=agg_rows_app, info_templates=agg_rows_templates, list_users = list_users)


@app.route("/create_template", methods=["GET", "POST"])
@login_required
@admin_required

def create_template():
    """Create a week schedule template for a specialist"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure specialist name was submitted
        if not request.form.get("specialist"):
            return apology("must provide specialist's name", 400)
        # Ensure service name was submitted
        if not request.form.get("service"):
            return apology("must provide name of service", 400)
        # Ensure day of week was submitted
        if not request.form.get("day"):
            return apology("must provide a day of week", 400)
        # Ensure time was submitted
        if not request.form.get("appt"):
            return apology("must provide a time slot", 400)

        # Find a service id
        service_id_rows = db.execute("SELECT id FROM services WHERE name = ?", request.form.get("service"))
        service_id = service_id_rows[0]['id']

        # Find a specialist id
        specialist_id_rows = db.execute("SELECT id FROM specialists WHERE firstlast = ?", request.form.get("specialist"))
        specialist_id = specialist_id_rows[0]['id']

        # Create a new template
        db.execute("INSERT INTO schedule_templates (day, time, service_id, specialist_id, is_available) VALUES(?, ?, ?, ?, ?)",
                   request.form.get("day"), request.form.get("appt"), service_id, specialist_id, 1)

        # Redirect user to admin page
        return redirect("/admin")

# User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get info for dropdowns
        list_specialists = db.execute("SELECT firstlast FROM specialists")
        list_services = db.execute("SELECT name FROM services")
        return render_template("create-template.html", list_specialists=list_specialists, list_services=list_services)


@app.route("/create_schedule", methods=["GET", "POST"])
@login_required
@admin_required

def create_schedule():
    """Create an actual week schedule for a specialist based on their template"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure specialist name was submitted
        if not request.form.get("specialist"):
            return apology("must provide specialist's name", 400)
        # Ensure start date was submitted
        if not request.form.get("start_date"):
            return apology("must provide a start date of the week (Sunday)", 400)
        # Find a specialist id
        specialist_id_rows = db.execute("SELECT id FROM specialists WHERE firstlast = ?", request.form.get("specialist"))
        specialist_id = specialist_id_rows[0]['id']

        # Get the information about the templates chosen
        agg_rows_templates = db.execute("SELECT day, time, service_id, specialist_id, is_available\
            FROM schedule_templates WHERE specialist_id =  ?", specialist_id)

        # Create a new time slot for each template
        for row in agg_rows_templates:
            actual_date = set_date(request.form.get("start_date"), row["day"])  # Calculate actual date based on the day of week and starting date
            db.execute("INSERT INTO appointments (date, time, service_id, specialist_id, is_available) VALUES(?, ?, ?, ?, ?)",
                    actual_date, row["time"], row["service_id"], specialist_id, row["is_available"])

        # Redirect user to admin page
        return redirect("/admin")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get info for dropdowns
        list_specialists = db.execute("SELECT firstlast FROM specialists")
        return render_template("create-schedule.html", list_specialists=list_specialists)


@app.route("/create_appointment", methods=["GET", "POST"])
@login_required
@admin_required

def create_appointment():
    """Create an apointment for a client"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure date was submitted
        if not request.form.get("date"):
            return apology("must provide a date", 400)
        # Ensure time was submitted
        if not request.form.get("appt"):
            return apology("must provide a time", 400)
        # Ensure service's name was submitted
        if not request.form.get("service"):
            return apology("must provide name of service", 400)
        # Ensure specialist's name was submitted
        if not request.form.get("specialist"):
            return apology("must provide specialist's name", 400)
        # Ensure client's name was submitted
        if not request.form.get("client"):
            return apology("must provide client's name", 400)
        # Check the format of the date
        date_to_check = request.form.get("date")
        date_checked = date_for_db(date_to_check)
        # Find a service id
        service_id_rows = db.execute("SELECT id FROM services WHERE name = ?", request.form.get("service"))
        service_id = service_id_rows[0]['id']
        # Find a specialist's id
        specialist_id_rows = db.execute("SELECT id FROM specialists WHERE firstlast = ?", request.form.get("specialist"))
        specialist_id = specialist_id_rows[0]['id']
        # Find a client's id
        client_id_rows = db.execute("SELECT id FROM users WHERE username = ?", request.form.get("client"))
        user_id = client_id_rows[0]['id']
        # Check it time slot exist
        existing_slot_rows = db.execute("SELECT * FROM appointments WHERE date=? AND time=? AND specialist_id=?",
                    request.form.get("date"), request.form.get("appt"), specialist_id)
        if len(existing_slot_rows) == 0:
            # Create a new record
            db.execute("INSERT INTO appointments (date, time, service_id, specialist_id, client_id, is_available) VALUES(?, ?, ?, ?, ?, ?)",
                    date_checked, request.form.get("appt"), service_id, specialist_id, user_id, 1)
            # Redirect user to admin page
            return redirect("/admin")
        else:
            flash("Time slot exists for this time. Please use it or delete", "warning")
            # Redirect user to admin page
            return redirect("/admin")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get info for dropdowns
        list_specialists = db.execute("SELECT firstlast FROM specialists")
        list_services = db.execute("SELECT name FROM services")
        list_users = db.execute("SELECT username FROM users")

        return render_template("create-appointment.html", list_specialists=list_specialists,\
            list_services=list_services, list_users=list_users)


@app.route("/book_by_admin", methods=["GET", "POST"])
@login_required
@admin_required

def book_by_admin():
    """Create an apointment for a client for a particular row in Tab 1 Admin"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure id was submitted
        if not request.form.get("id"):
            return apology("must provide a id", 400)
        # Ensure client name was submitted
        if not request.form.get("client"):
            return apology("must provide a client's name", 400)
        # Find a client's id
        client_id_rows = db.execute("SELECT id FROM users WHERE username = ?", request.form.get("client"))
        user_id = client_id_rows[0]['id']
        # Update the database record
        db.execute("UPDATE appointments SET client_id = ? WHERE id = ?",
                    user_id, request.form.get("id"))
        # Redirect user to admin page
        return redirect("/admin")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get info for dropdown
        list_users = db.execute("SELECT username FROM users")

        # Populate a table with the info about the appointment chosen
        item_to_book = db.execute("SELECT ap.id, date, time, services.name AS service, specialists.firstlast AS specialist\
        FROM appointments AS ap\
        JOIN services ON ap.service_id = services.id\
        JOIN specialists ON ap.specialist_id = specialists.id\
        WHERE ap.id=?", request.args.get("id"))

        for row in item_to_book:
            row['date'] = change_format_date(row['date']) #Change date format for displaying in the table

        return render_template("book-by-admin.html", item_to_book=item_to_book, list_users=list_users)


@app.route("/delete_appointment", methods=["GET", "POST"])
@login_required
@admin_required

def delete_appointment():
    """Delete an apointment for a particular row in Tab 1 Admin"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure id was submitted
        if not request.form.get("id"):
            return apology("must provide a id", 400)
        # Update the database record
        db.execute("DELETE FROM appointments WHERE id = ?", request.form.get("id"))
        # Redirect user to admin page
        return redirect("/admin")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Populate a table with the info about the appointment chosen
        item_to_delete = db.execute("SELECT ap.id, date, time, services.name AS service, specialists.firstlast AS specialist\
        FROM appointments AS ap\
        JOIN services ON ap.service_id = services.id\
        JOIN specialists ON ap.specialist_id = specialists.id\
        WHERE ap.id=?", request.args.get("id"))

        for row in item_to_delete:
            row['date'] = change_format_date(row['date']) #Change date format for displaying in the table

        return render_template("delete-app.html", item_to_delete=item_to_delete)


@app.route("/delete_template", methods=["GET", "POST"])
@login_required
@admin_required

def delete_template():
    """Delete a shedule template for a particular row in Tab 2 Admin"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure id was submitted
        if not request.form.get("id"):
            return apology("must provide a id", 400)
        # Update the database record
        db.execute("DELETE FROM schedule_templates WHERE id = ?", request.form.get("id"))
        # Redirect user to admin page
        return redirect("/admin")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Populate a table with the info about the template chosen
        item_to_delete = db.execute("SELECT st.id, day, time, services.name AS service, specialists.firstlast AS specialist\
        FROM schedule_templates AS st\
        JOIN services ON st.service_id = services.id\
        JOIN specialists ON st.specialist_id = specialists.id\
        WHERE st.id=?", request.args.get("id"))

        for row in item_to_delete:
            row['day'] = get_day(row['day']) #Add day of week instead number

        return render_template("delete-template.html", item_to_delete=item_to_delete)


@app.route("/create_edit_user", methods=["GET", "POST"])
@login_required
@admin_required

def create_edit_user():
    """Change name or role for a user for a particular row in Tab 3 Admin"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("id"):
            return apology("must provide an ID", 400)
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide a user's name", 400)
        # Ensure is_admin was submitted
        if not request.form.get("is_admin"):
            return apology("must provide a user's role", 400)
        # Ensure is_specialist was submitted
        if not request.form.get("is_specialist"):
            return apology("must provide a user's role", 400)
        # Update the database record
        db.execute("UPDATE users SET username = ?, is_admin=?, is_specialist=? WHERE id = ? AND is_deleted IS NULL",
                    request.form.get("username"), request.form.get("is_admin"), request.form.get("is_specialist"), request.form.get("id"))
        # Redirect user to admin page
        return redirect("/admin")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Populate a table with the info about the user chosen
        user_edit = db.execute("SELECT id, username, is_admin, is_specialist\
        FROM users WHERE id=? AND is_deleted IS NULL", request.args.get("userId"))
        #Change Yes/No format for displaying in the table
        for row in user_edit:
            row['is_admin'] = get_yes_no(row['is_admin'])
            row['is_specialist'] = get_yes_no(row['is_specialist'])
        return render_template("create-edit-user.html", user_edit=user_edit)

@app.route("/delete_user", methods=["GET", "POST"])
@login_required
@admin_required

def delete_user():
    """Delete a user for a particular row in Tab 3 Admin"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("id"):
            return apology("must provide an ID", 400)
        # Update the database record - mark the user as deleted
        db.execute("UPDATE users SET is_deleted = ? WHERE id = ? AND is_deleted IS NULL",
                    1, request.form.get("id"))
        # Redirect user to admin page
        return redirect("/admin")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Populate a table with the info about the user chosen
        user_delete = db.execute("SELECT id, username, is_admin, is_specialist\
        FROM users WHERE id=? AND is_deleted IS NULL", request.args.get("userId"))
        #Change Yes/No format for displaying in the table
        for row in user_delete:
            row['is_admin'] = get_yes_no(row['is_admin'])
            row['is_specialist'] = get_yes_no(row['is_specialist'])
        return render_template("delete-user.html", user_delete=user_delete)