import unittest
from pathlib import Path
from custom.utils import validate_relative_path
from custom.exceptions import ValidationError

class TestUtils(unittest.TestCase):
    def test_validate_relative_path_safe(self):
        validate_relative_path("safe/path.txt")
        validate_relative_path("file.txt")
    
    def test_validate_relative_path_unsafe(self):
        import os
        with self.assertRaises(ValidationError):
            validate_relative_path("../unsafe.txt")
        
        abs_path = os.path.abspath("unsafe.txt")
        with self.assertRaises(ValidationError):
            validate_relative_path(abs_path)

if __name__ == '__main__':
    unittest.main()
