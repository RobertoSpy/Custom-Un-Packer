import unittest
import os
import shutil
import tempfile
import time
from custom.packer import Packer
from custom.unpacker import Unpacker

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.src_dir = os.path.join(self.test_dir, "src")
        self.out_dir = os.path.join(self.test_dir, "out")
        self.archive_path = os.path.join(self.test_dir, "test.roby")
        
        os.makedirs(self.src_dir)
        os.makedirs(self.out_dir)
        
        # Create dummy files
        self.files = {
            "file1.txt": b"content1",
            "sub/file2.bin": b"\x00\x01\x02",
        }
        
        for p, content in self.files.items():
            full_p = os.path.join(self.src_dir, p)
            os.makedirs(os.path.dirname(full_p), exist_ok=True)
            with open(full_p, 'wb') as f:
                f.write(content)
            # Set specific mtime
            os.utime(full_p, (1600000000, 1600000000))

    def tearDown(self):
      try:
        shutil.rmtree(self.test_dir)
      except:
        pass

    def test_full_cycle(self):
        # Pack
        packer = Packer()
        packer.pack(self.src_dir, self.archive_path)
        
        self.assertTrue(os.path.exists(self.archive_path))
        
        # Unpack
        unpacker = Unpacker()
        unpacker.unpack(self.archive_path, self.out_dir)
        
        # Verify
        for p, content in self.files.items():
            out_p = os.path.join(self.out_dir, p)
            self.assertTrue(os.path.exists(out_p))
            
            with open(out_p, 'rb') as f:
                self.assertEqual(f.read(), content)
                
            stat = os.stat(out_p)
            self.assertEqual(int(stat.st_mtime), 1600000000)

    def test_selective_unpack(self):
        packer = Packer()
        packer.pack(self.src_dir, self.archive_path)
        
        unpacker = Unpacker()
        # Extract only file1.txt
        unpacker.unpack(self.archive_path, self.out_dir, ["file1.txt"])
        
        self.assertTrue(os.path.exists(os.path.join(self.out_dir, "file1.txt")))
        self.assertFalse(os.path.exists(os.path.join(self.out_dir, "sub/file2.bin")))

if __name__ == '__main__':
    unittest.main()
