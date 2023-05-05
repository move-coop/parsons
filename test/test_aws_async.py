import unittest
from test.utils import assert_matching_tables

from parsons import Table
from parsons.aws.aws_async import import_and_get_task, get_func_task_path
from parsons.aws.lambda_distribute import distribute_task


def fake_func(arg1, arg2, kwarg1=None, kwarg2=56):
    return (arg1, arg2, kwarg1, kwarg2)


count = 0
tableargs = (None, None)


def fake_table_process(table, **fakekwargs):
    global count
    global tableargs
    count = count + 1
    tableargs = (table, fakekwargs)


class FakeRunner(object):
    def __init__(self, init1=None):
        self.init1 = init1

    def foobar(self, table, a, x=None, y=None):
        global count
        global tableargs
        count = count + 1
        tableargs = (table, self.init1, a, x, y)
        if a == "raise":
            raise Exception("foo bar")


class TestAsync(unittest.TestCase):
    def test_task_path_conversion(self):
        # fake_func
        fake_str = get_func_task_path(fake_func)
        print("fake_str", fake_str)
        fake_renewed = import_and_get_task(fake_str)
        self.assertEqual(fake_renewed(1, 2, 3), (1, 2, 3, 56))

        # Table.from_csv_string @classmethod
        csv_str = get_func_task_path(Table.from_csv_string, Table)
        print("csv_str", csv_str)
        csv_renewed = import_and_get_task(csv_str)
        assert_matching_tables(csv_renewed("x,y\n1,2"), Table([("x", "y"), ("1", "2")]))

        # Table.to_dicts (instance)
        dicts_str = get_func_task_path(Table.to_dicts, Table)
        print("dicts_str", dicts_str)
        dicts_renewed = import_and_get_task(dicts_str, {"lst": [("x", "y"), (1, 2)]})
        self.assertEqual(dicts_renewed(), [{"x": 1, "y": 2}])

    def test_distribute_task(self):
        global count
        global tableargs
        datatable = [
            ("x", "y"),
            (1, 2),
            (3, 4),
            (5, 6),
            (7, 8),
            (9, 0),
            (11, 12),
            (13, 14),
            (15, 16),
            (17, 18),
            (19, 10),
        ]
        count = 0
        tableargs = None
        distribute_task(
            Table(datatable),
            fake_table_process,
            "foo",  # bucket
            group_count=5,
            storage="local",
            func_kwargs={"x": 1, "y": [2, 3]},
        )
        self.assertEqual(count, 2)
        assert_matching_tables(
            tableargs[0],
            Table(
                [
                    ("x", "y"),
                    ("11", "12"),
                    ("13", "14"),
                    ("15", "16"),
                    ("17", "18"),
                    ("19", "10"),
                ]
            ),
        )
        count = 0
        tableargs = None
        distribute_task(
            Table(datatable + [(0, 0)]),
            FakeRunner.foobar,
            "foo",  # bucket
            group_count=5,
            storage="local",
            func_class=FakeRunner,
            func_class_kwargs={"init1": "initx"},
            func_kwargs={"a": 1, "x": 2, "y": 3},
        )
        self.assertEqual(count, 3)
        self.assertEqual(tableargs[1:], ("initx", 1, 2, 3))
        self.assertEqual(tableargs[1:], ("initx", 1, 2, 3))
        assert_matching_tables(tableargs[0], Table([("x", "y"), ("0", "0")]))

        # 3. catch=True (with throwing)
        count = 0
        tableargs = None
        distribute_task(
            Table(datatable[:6]),
            FakeRunner.foobar,
            "foo",  # bucket
            group_count=5,
            storage="local",
            func_class=FakeRunner,
            func_class_kwargs={"init1": "initx"},
            catch=True,
            func_kwargs={"a": "raise", "x": 2, "y": 3},
        )
