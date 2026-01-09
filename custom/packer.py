import os
import struct
import logging
from .format import Header, IndexEntry
from .utils import validate_relative_path, calculate_checksum
from .exceptions import ValidationError

class Packer:
    def pack(self, target_dir: str, archive_path: str):
        logging.info(f"Packing '{target_dir}' into '{archive_path}'...")
        
        files_metadata = [] 
        
        logging.debug(f"Target directory: {target_dir}")
        logging.debug(f"Archive path: {archive_path}")
        
        with open(archive_path, 'wb') as archive:
            # 1. Write Placeholder Header
         
            placeholder_header = Header(file_count=0, index_offset=0)
            archive.write(placeholder_header.pack())
            
            # 2. Walk directory
            
            for root, dirs, files in os.walk(target_dir):
                dirs.sort() 
                files.sort()
                
                for filename in files:
                    full_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(full_path, target_dir)
                    
                    validate_relative_path(relative_path)
                    
                
                    clean_path = relative_path.replace(os.sep, '/')
                    
                    current_offset = archive.tell()
                    file_size = 0
                    
                    import hashlib
                    sha256 = hashlib.sha256()
                    
                    # Capture metadata
                    stat_info = os.stat(full_path)
                    mtime = stat_info.st_mtime
                    mode = stat_info.st_mode
                    
                    logging.debug(f"Processing: {full_path} -> {clean_path}")
                    logging.debug(f"  Stat: mtime={mtime}, mode={mode:o}")
                    
                    with open(full_path, 'rb') as f:
                        while True:
                            chunk = f.read(65536) 
                            if not chunk:
                                break
                            archive.write(chunk)
                            sha256.update(chunk)
                            file_size += len(chunk)
                            
                    checksum = sha256.digest()
                    logging.debug(f"  Checksum (SHA256): {checksum.hex()}")
                    
                    files_metadata.append(IndexEntry(
                        path=clean_path,
                        file_size=file_size,
                        content_offset=current_offset,
                        checksum=checksum,
                        mtime=mtime,
                        mode=mode
                    ))
                    
                    logging.info(f"  Added: {clean_path} ({file_size} bytes)")

            # 3. Write Index
            index_offset_start = archive.tell()
            for entry in files_metadata:
                archive.write(entry.pack())
                
            # 4. Rewrite Header with correct info
            archive.seek(0)
            final_header = Header(
                file_count=len(files_metadata),
                index_offset=index_offset_start
            )
            archive.write(final_header.pack())
            
        logging.info(f"Done. Archive created: {archive_path}")
