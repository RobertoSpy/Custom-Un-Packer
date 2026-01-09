import os
import logging
from .format import Header, IndexEntry
from .exceptions import FormatError

class Unpacker:
    def list_content(self, archive_path: str):
        
        if not os.path.exists(archive_path):
             logging.error(f"Error: Archive not found: {archive_path}")
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
             logging.error(f"Error reading archive: {e}")
        except Exception as e:
             logging.error(f"Unexpected error: {e}")

    def unpack(self, archive_path: str, output_dir: str = '.', specific_files: list = None):
         if output_dir is None: output_dir = '.'
         if specific_files is None: specific_files = []
         
         targets = set(specific_files)
         
         if not os.path.exists(archive_path):
              logging.error(f"Error: Archive not found: {archive_path}")
              return

         try:
            import hashlib
            with open(archive_path, 'rb') as f:
                header_data = f.read(14)
                header = Header.unpack(header_data)
                logging.debug(f"Header Validated. Ver={header.version}, Files={header.file_count}, IndexOffset={header.index_offset}")
                
                f.seek(header.index_offset)
                entries = []
                for _ in range(header.file_count):
                    entries.append(IndexEntry.read(f))
                
                files_to_extract = []
                found_paths = set()
                
                for entry in entries:
                    if not targets or entry.path in targets:
                        files_to_extract.append(entry)
                        found_paths.add(entry.path)
                        
                if targets:
                    missing = targets - found_paths
                    for m in missing:
                        logging.warning(f"File not found in archive: {m}")
                        
                for entry in files_to_extract:
                    # Basic path safety
                    if '..' in entry.path or entry.path.startswith('/') or entry.path.startswith('\\'):
                         logging.warning(f"Skipping potential unsafe path: {entry.path}")
                         continue
                         
                    dest_path = os.path.join(output_dir, entry.path)
                    dest_dir = os.path.dirname(dest_path)
                    
                    if dest_dir:
                        os.makedirs(dest_dir, exist_ok=True)
                        
                    f.seek(entry.content_offset)
                    
                    sha256 = hashlib.sha256()
                    remaining = entry.file_size
                    
                    with open(dest_path, 'wb') as out_f:
                        while remaining > 0:
                            chunk_size = min(65536, remaining)
                            data = f.read(chunk_size)
                            if not data:
                                raise FormatError(f"Unexpected EOF content for {entry.path}")
                            sha256.update(data)
                            out_f.write(data)
                            remaining -= len(data)
                            
                    if sha256.digest() != entry.checksum:
                        logging.error(f"Checksum BAD: {entry.path}")
                        logging.debug(f"  Expected: {entry.checksum.hex()}")
                        logging.debug(f"  Computed: {sha256.digest().hex()}")
                    else:
                        logging.info(f"Extracted: {entry.path}")
                        logging.debug(f"  Restoring mtime={entry.mtime}, mode={entry.mode:o}")
                        
                    # Restore Metadata
                    try:
                        os.utime(dest_path, (entry.mtime, entry.mtime))
                        os.chmod(dest_path, entry.mode)
                    except Exception as e:
                        logging.warning(f"Metadata warning for {entry.path}: {e}")
                        
         except FormatError as e:
              logging.error(f"Archive Format Error: {e}")
         except Exception as e:
              logging.error(f"Extraction Error: {e}")
         
