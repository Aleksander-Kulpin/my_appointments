import datetime

def set_date(start_date, delta_days):
    # giving the date format for input from HTML
    date_format1 = '%Y-%m-%d'

    # giving the date format for database record
    date_format2 = '%d-%m-%Y'

    # formatting the date using strptime() function and subtracting 2 days from it
    date = datetime.datetime.strptime(start_date, date_format1) + datetime.timedelta(delta_days)

    # Formatting the date
    date=date.strftime(date_format2)
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

def compare_date(first_date, second_date):
    # formatting
    first_formatted = datetime.datetime.strptime(first_date, '%Y-%m-%d')
    second_formatted = datetime.datetime.strptime(second_date, '%Y-%m-%d')
    # If first date is earlier than the second, return True
    if first_formatted < second_formatted:
        return True
    else:
        return False

def date_before_current(date, time):
    # formatting
    date_time = date + " " + time
    date_time_formatted = datetime.datetime.strptime(date_time, '%Y-%m-%d %I:%M %p')
    print(date_time)
    # If first date is earlier than the current date and time, return True
    if date_time_formatted < datetime.datetime.now():
        return True
    else:
        return False

date = '2022-12-10'
print(date_for_db(date))