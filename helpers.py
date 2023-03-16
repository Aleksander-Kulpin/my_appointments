from flask import redirect, render_template, session, flash
from functools import wraps
from cs50 import SQL
import datetime

db = SQL("sqlite:///myapp.db")

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Modified login_required decorator to restrict access to admin group.
    """
    @wraps(f)
    def decorated_view1(*args, **kwargs):

        # Check which user has logged in
        current_user_id = session["user_id"]

        # Query database for user role
        rows = db.execute("SELECT is_admin FROM users WHERE id = ?", current_user_id)
        is_admin = rows[0]["is_admin"]

        if is_admin == False:        # user is not an Admin
            flash("You don't have permission to access Admin Portal.", "warning")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_view1

def specialist_required(f):
    """
    Modified login_required decorator to restrict access to admin group.
    """
    @wraps(f)
    def decorated_view2(*args, **kwargs):

        # Check which user has logged in
        current_user_id = session["user_id"]

        # Query database for user role
        rows = db.execute("SELECT is_specialist FROM users WHERE id = ?", current_user_id)
        is_specialist = rows[0]["is_specialist"]

        if is_specialist == False:        # user is not a specialist
            flash("You don't have permission to access Specialist's Portal.", "warning")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_view2

def get_day(day):
    if day == 0:
        return "Sunday"
    elif day == 1:
        return "Monday"
    elif day == 2:
        return "Tuesday"
    elif day == 3:
        return "Wednesday"
    elif day == 4:
        return "Thursday"
    elif day == 5:
        return "Friday"
    elif day == 6:
        return "Saturday"

def get_yes_no(number):
    if number == 0:
        return "No"
    elif number == 1:
        return "Yes"

def set_date(start_date, delta_days):
    # giving the date format for input
    date_format1 = '%Y-%m-%d'

    # formatting the date using strptime() function and subtracting 2 days from it
    date = datetime.datetime.strptime(start_date, date_format1) + datetime.timedelta(delta_days)

    # Formatting the date
    date=date.strftime(date_format1)
    return date

def change_format_date(date_from_db):
    x = datetime.datetime.strptime(date_from_db, '%Y-%m-%d')
    return x.strftime("%b %d %Y")

def date_for_db(date_from_form):
    try:
        x = datetime.datetime.strptime(date_from_form, '%b %d %Y')
        return x.strftime("%Y-%m-%d")
    except ValueError:
        return date_from_form

def date_before_current(date, time):
    # formatting
    date_time = date + " " + time
    date_time_formatted = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M')
    print(date_time)
    # If first date is earlier than the current date and time, return True
    if date_time_formatted < datetime.datetime.now():
        return True
    else:
        return False
