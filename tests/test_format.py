import unittest
import struct
from custom.format import Header, IndexEntry, HEADER_FORMAT, MAGIC_BYTES, VERSION, ENTRY_METADATA_FMT
from custom.exceptions import FormatError

class TestHeader(unittest.TestCase):
    def test_pack_unpack(self):
        h = Header(file_count=10, index_offset=12345)
        data = h.pack()
        self.assertEqual(len(data), struct.calcsize(HEADER_FORMAT))
        
        h2 = Header.unpack(data)
        self.assertEqual(h2.file_count, 10)
        self.assertEqual(h2.index_offset, 12345)
        self.assertEqual(h2.magic, MAGIC_BYTES)
        self.assertEqual(h2.version, VERSION)

    def test_invalid_magic(self):
        bad_data = struct.pack(HEADER_FORMAT, b'BAD!', 1, 0, 0)
        with self.assertRaises(FormatError):
            Header.unpack(bad_data)

class TestIndexEntry(unittest.TestCase):
    def test_pack_read(self):
        from io import BytesIO
        
        entry = IndexEntry(
            path="test/file.txt",
            file_size=100,
            content_offset=5000,
            checksum=b'A'*32,
            mtime=1700000000.0,
            mode=0o644
        )
        data = entry.pack()
        
        stream = BytesIO(data)
        entry2 = IndexEntry.read(stream)
        
        self.assertEqual(entry2.path, "test/file.txt")
        self.assertEqual(entry2.file_size, 100)
        self.assertEqual(entry2.content_offset, 5000)
        self.assertEqual(entry2.checksum, b'A'*32)
        self.assertEqual(entry2.mtime, 1700000000.0)
        self.assertEqual(entry2.mode, 0o644)

if __name__ == '__main__':
    unittest.main()
