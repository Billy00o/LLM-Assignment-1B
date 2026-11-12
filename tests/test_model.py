import ast
import re
import unittest

import torch

from src.model import get_response, load_model


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model, cls.tokenizer = load_model()

    @classmethod
    def tearDownClass(cls):
        del cls.model, cls.tokenizer

    def test_gemma_cpu_bfloat16(self):
        self.assertEqual(self.model.config.model_type, "gemma")
        self.assertEqual(self.model.device.type, "cpu")
        self.assertEqual(self.model.dtype, torch.bfloat16)

    def test_factual_query(self):
        response = get_response(
            "What is the capital of France?", self.model, self.tokenizer, max_length=64
        )
        self.assertRegex(response.lower(), r"\bparis\b")

    def test_code_generation(self):
        response = get_response(
            "Write a short Python function named factorial(n) to calculate the factorial "
            "of a non-negative integer. Return only Python code.",
            self.model,
            self.tokenizer,
            max_length=128,
        )
        match = re.search(r"```(?:python)?\s*(.*?)```", response, re.IGNORECASE | re.DOTALL)
        source = match.group(1) if match else response
        # Parse syntax without executing model-generated code.
        tree = ast.parse(source.strip())
        self.assertTrue(
            any(isinstance(node, ast.FunctionDef) and node.name == "factorial" for node in tree.body),
            "Expected a top-level factorial function",
        )

    def test_blank_input(self):
        with self.assertRaisesRegex(ValueError, "Enter a non-empty question"):
            get_response(" ", self.model, self.tokenizer)


if __name__ == "__main__":
    unittest.main()
