# from py_base.ari_enum import TerritorySafety, get_enum
# from enum import Enum
import unittest
from pathlib import Path

from py_base.dbmanager import DatabaseManager
from py_system.tableobj import form_database_from_tableobjects


class TableTest(unittest.TestCase):

    def test_creation(self):

        self.test_database = DatabaseManager("unittest")
        
        form_database_from_tableobjects(self.test_database)

        self.test_database.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.test_database.cursor.fetchall()

        self.assertEqual(len(tables), 9)



if __name__ == "__main__":
    unittest.main()

    # (Path.cwd() / "data/unittest.db").unlink()