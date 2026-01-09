import struct
from .constants import HEADER_FORMAT, MAGIC_BYTES, VERSION, ENTRY_METADATA_FMT, ENTRY_METADATA_SIZE, HEADER_SIZE
from .exceptions import FormatError

class Header:
    def __init__(self, file_count, index_offset):
        self.magic = MAGIC_BYTES
        self.version = VERSION
        self.file_count = file_count
        self.index_offset = index_offset

    def pack(self) -> bytes:
        return struct.pack(HEADER_FORMAT, self.magic, self.version, self.file_count, self.index_offset)

    @classmethod
    def unpack(cls, data: bytes):
        if len(data) < HEADER_SIZE:
             raise FormatError("Data too short for header")
        
        magic, version, file_count, index_offset = struct.unpack(HEADER_FORMAT, data)
        
        if magic != MAGIC_BYTES:
            raise FormatError(f"Invalid Magic Bytes: {magic}")
        
        
        return cls(file_count, index_offset)

class IndexEntry:
    def __init__(self, path: str, file_size: int, content_offset: int, checksum: bytes, mtime: float = 0.0, mode: int = 0):
        self.path = path
        self.file_size = file_size
        self.content_offset = content_offset
        self.checksum = checksum
        self.mtime = mtime
        self.mode = mode
        
    def pack(self) -> bytes:
        path_bytes = self.path.encode('utf-8')
        path_len = len(path_bytes)
        
        header = struct.pack('<H', path_len)
        metadata = struct.pack(ENTRY_METADATA_FMT, self.file_size, self.content_offset, self.checksum, self.mtime, self.mode)
        return header + path_bytes + metadata

    @classmethod
    def read(cls, stream):
        
        path_len_data = stream.read(2)
        if len(path_len_data) < 2:
            raise FormatError("Unexpected End of File reading Index Entry")
        path_len = struct.unpack('<H', path_len_data)[0]
        
        path_bytes = stream.read(path_len)
        if len(path_bytes) < path_len:
             raise FormatError("Unexpected EOF reading Index Path")
        path = path_bytes.decode('utf-8')
        
        fixed_data = stream.read(ENTRY_METADATA_SIZE)
        if len(fixed_data) < ENTRY_METADATA_SIZE:
             raise FormatError("Unexpected EOF reading Index Metadata")
             
        file_size, content_offset, checksum, mtime, mode = struct.unpack(ENTRY_METADATA_FMT, fixed_data)
        
        return cls(path, file_size, content_offset, checksum, mtime, mode)
