import sqlite3

from userabc import UserABC


class Customer(UserABC):
    ACCOUNT_TABLE_NAME = "customers"
    ACCOUNT_ID_COLUMN_NAME = "cid"

    def __init__(self, cursor: sqlite3.Cursor, cid: str):
        super().__init__({
            "Start a session": None,
            "Search for movies": self.search_for_movies,
            "End watching a movie": None,
            "End the session": None,
        }, cursor, cid)

    def search_for_movies(self):
        """
        this should give a good model:

        SELECT title, ((title LIKE '%shaw%') + (title LIKE '%morgan%') +
                       (c.role LIKE '%shaw%') + (c.role LIKE '%morgan%') +
                       (mP.name LIKE '%shaw%') + (mP.name LIKE '%morgan%')) matching_terms
        FROM movies
                 JOIN casts c on movies.mid = c.mid
                 JOIN moviePeople mP on c.pid = mP.pid
        WHERE matching_terms > 1
        GROUP BY title
        ORDER BY matching_terms DESC;


        Returns:

        """
        pass