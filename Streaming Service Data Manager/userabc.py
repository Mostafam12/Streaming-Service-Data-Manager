import sqlite3
from getpass import getpass
from typing import Callable, Dict

from utils import run_from_list


class UserABC:
    ACCOUNT_TABLE_NAME = ...
    ACCOUNT_ID_COLUMN_NAME = ...

    def __init__(self, options: Dict[str, Callable], cursor: sqlite3.Cursor, _id: str):
        """
        Represents a high-level user abstract base class, whether it be an editor or customer
        Args:
            options: dictionary of the name of the option and the function that handles that option
        """
        self._id = _id
        self.options = options
        self.cursor = cursor

    def choose_options(self):
        """
        Prints out all the options and prompts the user for input. Runs the option chosen

        Returns:
            None
        """
        run_from_list("Choose from the following options:", self.options)

    def authenticate(self):
        """
        Prompts a user to authenticate their account until they get it correct.

        Returns:
            None
        """
        prompt_text = f"Please enter your password for {self._id} (input is hidden):"
        while True:
            # warning: getpass sometimes doesn't show the prompt at all :\
            pwd = getpass(prompt_text)
            if not self.cursor.execute(
                f"SELECT true FROM {self.ACCOUNT_TABLE_NAME} WHERE {self.ACCOUNT_ID_COLUMN_NAME} = ? AND pwd = ?",
                (self._id, pwd),
            ).fetchone():
                print("Incorrect password")
            else:
                break
