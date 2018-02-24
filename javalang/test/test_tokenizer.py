import unittest
from .. import tokenizer


class TestTokenizer(unittest.TestCase):

    def test_tokenizer(self):

        # Given
        code = "    @Override"

        # When
        tokens = list(tokenizer.tokenize(code))

        # Then
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].value, "@")
        self.assertEqual(tokens[1].value, "Override")
        self.assertEqual(type(tokens[0]), tokenizer.Annotation)
        self.assertEqual(type(tokens[1]), tokenizer.Identifier)
