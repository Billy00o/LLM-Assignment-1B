import unittest
from src.model import build_messages

class LogicTests(unittest.TestCase):
    def test_blank(self):
        with self.assertRaises(ValueError): build_messages(" ")
    def test_modes(self):
        self.assertIn("practice question", build_messages("fractions", mode="quiz")[0]["content"])
    def test_history_not_mutated(self):
        h = [{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello"}]
        result = build_messages("Next", h)
        self.assertEqual(len(h), 2)
        self.assertEqual(len(result), 3)
    def test_invalid_history(self):
        with self.assertRaises(ValueError): build_messages("Hi", [{"role":"assistant","content":"x"}])
