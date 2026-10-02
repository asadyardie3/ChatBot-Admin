import unittest
from command_parser import parse


class ParserTests(unittest.TestCase):
    def test_add(self):
        r = parse('can you add the user "john.smith@xyz.com" with phone number "+92332"')
        self.assertEqual(r, {"action": "add", "email": "john.smith@xyz.com", "phone": "+92332"})

    def test_remove(self):
        r = parse('can you remove the user "john.smith@xyz.com"')
        self.assertEqual(r, {"action": "delete", "who": "john.smith@xyz.com"})

    def test_update(self):
        r = parse("can you update samanthas city to Cordoba")
        self.assertEqual(r, {"action": "update", "who": "samanthas", "field": "city", "value": "Cordoba"})

    def test_list(self):
        self.assertEqual(parse("list users")["action"], "list")

    def test_unknown(self):
        self.assertEqual(parse("hello there")["action"], "unknown")


if __name__ == "__main__":
    unittest.main()
