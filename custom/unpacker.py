import os
from .format import Header, IndexEntry
from .exceptions import FormatError

class Unpacker:
    def list_content(self, archive_path: str):
        
        if not os.path.exists(archive_path):
             print(f"Error: Archive not found: {archive_path}")
             return

        try:
            with open(archive_path, 'rb') as f:
                # 1. Read Header
                header_data = f.read(14)
                header = Header.unpack(header_data)
                
                print(f"Archive: {archive_path}")
                print(f"Files: {header.file_count}")
                print("-" * 60)
                print(f"{'File Name':<40} | {'Size (bytes)':>15}")
                print("-" * 60)
                
                # 2. Jump to Index
                f.seek(header.index_offset)
                
                # 3. Read Entries
                for _ in range(header.file_count):
                    entry = IndexEntry.read(f)
                    print(f"{entry.path:<40} | {entry.file_size:>15,}")
                    
                print("-" * 60)
                
        except FormatError as e:
             print(f"Error reading archive: {e}")
        except Exception as e:
             print(f"Unexpected error: {e}")

    def unpack(self, archive_path: str, output_dir: str = None):
         print(f"Unpacker stub: Phase 4 will implement extraction.")
         
