import csv
import io
import unittest

from exporter import export_row


class ExportTests(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(export_row(["a", "b"]), "a,b\n")

    def test_comma(self):
        self.assertEqual(export_row(["a,b", "c"]), '"a,b",c\n')

    def test_quote(self):
        self.assertEqual(export_row(['a"b', "c"]), '"a""b",c\n')

    def test_round_trip(self):
        values = ["a\nb", "c,d", 'e"f', ""]
        self.assertEqual(list(csv.reader(io.StringIO(export_row(values)))), [values])


if __name__ == "__main__":
    unittest.main()
