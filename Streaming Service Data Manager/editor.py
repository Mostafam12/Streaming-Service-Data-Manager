from datetime import datetime

from userabc import UserABC
from utils import (
    get_clamped_int,
    get_movie_title,
    cls,
    get_yes_no,
    get_unique,
    get_string_with_restricted_length,
    pause,
    get_choice_from_list, run_from_list,
)


class Editor(UserABC):
    ACCOUNT_TABLE_NAME = "editors"
    ACCOUNT_ID_COLUMN_NAME = "eid"

    def __init__(self, cursor, eid):
        super().__init__(
            {"Add a movie": self.add_movie, "Update a recommendation": self.update_recommendation}, cursor, eid
        )

    def add_movie(self):
        mid = get_unique("Enter a unique movie ID: ", "movies", "mid", self.cursor, prompter=get_clamped_int, low=0)
        title = get_movie_title()
        # 1888 is the earliest movie according to google
        year = get_clamped_int("Enter the movie year: ", 1888, datetime.now().year)
        # longest movie was apparently 873min. let's leave some headroom here
        runtime = get_clamped_int("Enter the runtime in minutes: ", 1, 1000)
        cast_ids = self._select_cast_members()

        self.cursor.execute("INSERT INTO movies values (?, ?, ?, ?)", (mid, title, year, runtime))
        # mid is the same for all the casts, hence why we repeat it
        for cast_id, role_name in cast_ids.items():
            self.cursor.execute("INSERT INTO casts values (?, ?, ?)", (mid, cast_id, role_name))

        # this is what actually saves all of our stuff
        self.cursor.connection.commit()
        pause(f"The movie '{title}' has been created. Press enter to continue")

    def update_recommendation(self):
        choices = ["All-Time", "Year", "Month"]
        operand_idx = get_choice_from_list("Choose a timeseries", choices)
        if choices[operand_idx] == "Year":
            day_delta = 365
        elif choices[operand_idx] == "Month":
            day_delta = 30
        else:  # alltime
            # just need a big enough integer
            day_delta = 2 ** 32

        # this is either really dumb or really smart im not sure which it is
        # uses our custom sorted_concat function to eliminate duplicates pairs like m1/m2, m2/m1
        recs = self.cursor.execute(
        """-- noinspection SqlResolve @ routine/"sorted_concat"
        SELECT m1.mid, m2.mid, COUNT(DISTINCT cust.cid), IIF(r.recommended, true, false)
        FROM customers cust
                 JOIN sessions s1 on cust.cid = s1.cid
                 JOIN watch w1 on w1.sid = s1.sid
                 JOIN movies m1 on m1.mid = w1.mid
        
                 JOIN sessions s2 on cust.cid = s2.cid AND s2.sid != s1.sid
                 JOIN watch w2 on w2.sid = s2.sid AND w1.mid != w2.mid
                 JOIN movies m2 on m2.mid = w2.mid
        
                 LEFT JOIN recommendations r on (m1.mid = r.watched AND m2.mid = r.recommended) OR
                                                (m2.mid = r.watched AND m1.mid = r.recommended)
        WHERE w1.duration >= m1.runtime / 2.0
          AND w2.duration >= m2.runtime / 2.0
          AND JULIANDAY(datetime('now')) - JULIANDAY(s1.sdate) < ?
          AND JULIANDAY(datetime('now')) - JULIANDAY(s2.sdate) < ?
        GROUP BY sorted_concat(m1.mid, m2.mid)
        ORDER BY COUNT(DISTINCT cust.cid);
        """, (day_delta, day_delta)).fetchall()

        formatted_choices = []
        in_recommended_texts = ["pair not in recommended", "pair in recommended"]
        for m1_mid, m2_mid, count, in_recs in recs:
            formatted_choices.append(f"{m1_mid}/{m2_mid} | {count} have watched | {in_recommended_texts[in_recs]}")
        cls()
        operand_idx = get_choice_from_list("Choose a pair to operate on: ", formatted_choices)
        m1_mid, m2_mid, *_ = choices[operand_idx]

        run_from_list("Choose what operation you would like to perform", {
            f"Update or add item ({m1_mid}/{m2_mid}) in recommendations": self._upsert_recommended_pair,
            f"Delete pair ({m1_mid}/{m2_mid}) from recommendations": self._delete_from_recommended
        }, wid=m1_mid, rid=m2_mid)

    def _delete_from_recommended(self, wid: int, rid: int):
        if get_yes_no(f"Are you sure you want to delete the pair {wid}/{rid}? [Y/n] "):
            # need to catch both permutations of watched/recommended
            self.cursor.execute(
                "DELETE FROM recommendations WHERE watched=? AND recommended=? OR watched=? AND recommended=?",
                (wid, rid, rid, wid)).connection.commit()
        else:
            print("operation aborted?")

    def _upsert_recommended_pair(self, wid: int, rid: int):
        pass

    def _select_cast_members(self) -> None:
        """
        Takes care of the selecting cast members sub-task.
        Allows for adhoc creation of movie people to use them as case member
        """
        roles = {}
        cast_id_prompt = (
            "Enter a unique cast ID. If it doesn't currently exist you will be prompted for creation.\n"
            "You may enter -1 to exit this selection and return to the previous menu:"
        )
        # get as many cast members as they want to enter
        cls()
        roles_text = "\n"
        while (
                cur_cast_id := get_string_with_restricted_length(
                    message=f"Current cast member IDs: {roles_text}\n{cast_id_prompt}", length=4
                )
        ) != "-1":
            cast_details = self.cursor.execute(
                "SELECT name, birthYear FROM moviePeople WHERE pid=?", (cur_cast_id,)
            ).fetchone()
            if cast_details is not None:
                name, birth_year = cast_details
                print(f"Name      : {name}\n" f"Birth Year: {birth_year}")
            elif get_yes_no(message=f"{cur_cast_id} does not exist. Create them? [Y/n]"):
                name = input("Name: ")
                birth_year = get_clamped_int(message="Birth Year: ", low=1700, high=datetime.now().year)
                if not get_yes_no(
                        message=f'Create movie person with ID {cur_cast_id}, name of "{name}" born {birth_year}? [Y/n]'
                ):
                    continue
                self.cursor.execute("INSERT INTO moviePeople values (?, ?, ?)", (cur_cast_id, name, birth_year))
            else:
                continue
            role = input(f"Enter a role name for {name} ({cur_cast_id}): ")
            roles[cur_cast_id] = role
            roles_text = "\n" + "\n ".join(f"({pid}) {role_name}" for pid, role_name in roles.items())
            cls()
        return roles
