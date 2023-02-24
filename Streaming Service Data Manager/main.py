import sqlite3
from datetime import datetime

from customer import Customer
from editor import Editor
from utils import get_clamped_int, get_string_with_restricted_length, sqlite3_sort_concat_2_fields


def main():
    con = sqlite3.connect("./a2.db", detect_types=sqlite3.PARSE_COLNAMES)  # todo: dehardcode me
    con.create_function("sorted_concat", -1, sqlite3_sort_concat_2_fields, deterministic=True)
    cursor = con.cursor()

    # initializes the database if not already done
    with open("init.sql") as init:
        cursor.executescript(init.read())

    while True:
        _id = get_string_with_restricted_length(
            "Enter an existing cID/eID, or the cID of the customer account you would like to create: ", 4)
        is_customer = cursor.execute("SELECT true FROM customers WHERE cid == ?", (_id,)).fetchone()
        is_editor = cursor.execute("SELECT true FROM editors WHERE eid == ?", (_id,)).fetchone()
        if not any((is_customer, is_editor)):
            print("You didn't enter a valid cID or eID")
            continue

        if is_customer:
            # todo: make a customer account here
            user = Customer(cursor, _id)

        else:
            user = Editor(cursor, _id)

        user.authenticate()
        user.choose_options()


if __name__ == '__main__':
    main()