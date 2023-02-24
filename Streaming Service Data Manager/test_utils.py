import io
import sqlite3

from utils import cls, get_yes_no, get_non_empty_input, get_input_of_arbitrary_type, get_string_with_restricted_length, \
    pause, get_choice_from_list, run_from_list, get_clamped_int, get_unique


class TestUtils:
    def test_cls_doesnt_crash(self):
        print("aksdffhlaksdhj")
        # no way to check if this worked or not - just checking if it crashes kek
        cls()

    def test_get_yes_no(self, monkeypatch):
        buffer = io.StringIO("no\nn\n\nnotandanswer\nyes\ny\n\n")
        monkeypatch.setattr('sys.stdin', buffer)
        assert get_yes_no("") is False
        assert get_yes_no("") is False
        assert get_yes_no("", default=False) == False

        assert get_yes_no("")
        assert get_yes_no("")
        assert get_yes_no("")

    def test_get_non_empty_input(self, monkeypatch):
        buffer = io.StringIO()
        monkeypatch.setattr('sys.stdin', buffer)

        inp = "Asdfjkasdflkj"
        buffer.write(inp + "\n")
        buffer.seek(0)
        assert get_non_empty_input("") == inp

    def test_get_input_of_arbitrary_type(self, capsys, monkeypatch):
        monkeypatch.setattr('sys.stdin', io.StringIO("no\bno\nyes\n"))
        msg = "example error msg"

        def dummy(inp):
            assert inp == "yes", msg
            return True

        assert get_input_of_arbitrary_type("", dummy) is True

        captured = capsys.readouterr()
        assert msg in captured.out

    def test_get_string_with_restricted_length(self, capsys, monkeypatch):
        msg = "perfect length"
        monkeypatch.setattr('sys.stdin', io.StringIO(f"short\nreally long string\n{msg}\n"))

        assert get_string_with_restricted_length("", low=6, high=len(msg))

    def test_pause(self, monkeypatch):
        monkeypatch.setattr('sys.stdin', io.StringIO(f"\n"))
        assert pause("") is None

    def test_get_choice_from_list(self, monkeypatch):
        monkeypatch.setattr('sys.stdin', io.StringIO(f"7\n4\n"))

        assert get_choice_from_list("", range(4)) == 3

    def test_run_from_list(self, monkeypatch):
        monkeypatch.setattr('sys.stdin', io.StringIO(f"7\n1\n"))
        flag_dict = {}

        def set_flag(f):
            f["key"] = True

        run_from_list("", {"choice 1": set_flag}, f=flag_dict)
        assert flag_dict

    def test_get_clamped_int(self, monkeypatch):
        monkeypatch.setattr('sys.stdin', io.StringIO(f"7\n1\n4\n"))
        assert get_clamped_int("", 3, 6)

    def test_get_unique(self, monkeypatch):
        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE foo (id int primary key)")
        db.execute("INSERT INTO foo values(1)")
        db.execute("INSERT INTO foo values(2)")
        flag_dict = {}

        def prompter(_, f):
            f["key"] = True
            return input(_)

        monkeypatch.setattr('sys.stdin', io.StringIO(f"1\n2\n3\n"))
        assert get_unique("", table_name="foo", column_name="id", cursor=db, prompter=prompter, f=flag_dict) == '3'
        assert flag_dict
