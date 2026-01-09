import argparse
import sys
import logging
from .packer import Packer
from .unpacker import Unpacker
from .exceptions import CustomError
from .utils import validate_path


def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

def main():
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose debug logging')

    parser = argparse.ArgumentParser(description="Custom (Un)Packer Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Create command
    create_parser = subparsers.add_parser('create', parents=[parent_parser], help='Create a new archive')
    create_parser.add_argument('archive_name', help='Output archive path')
    create_parser.add_argument('target_dir', help='Directory to pack')

    # List command
    list_parser = subparsers.add_parser('list', parents=[parent_parser], help='List archive content')
    list_parser.add_argument('archive_name', help='Archive to list')

    # Extract command
    extract_parser = subparsers.add_parser('extract', parents=[parent_parser], help='Extract archive')
    extract_parser.add_argument('archive_name', help='Archive to extract')
    extract_parser.add_argument('files', nargs='*', help='Specific files to extract')
    extract_parser.add_argument('--output', '-o', help='Output directory', default='.')

    args = parser.parse_args()
    setup_logging(args.verbose)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'create':
          
            target = validate_path(args.target_dir)
            if not target.is_dir():
                raise CustomError(f"{target} is not a directory")
            
            archive_name = args.archive_name
            if not archive_name.endswith('.roby'):
                archive_name += '.roby'

            logging.info(f"Validation successful: Target '{target}' is a valid directory.")
            packer = Packer()
            packer.pack(str(target), archive_name)

        elif args.command == 'list':
            archive = validate_path(args.archive_name)
            unpacker = Unpacker()
            unpacker.list_content(str(archive))

        elif args.command == 'extract':
            archive = validate_path(args.archive_name)
            unpacker = Unpacker()
            unpacker.unpack(str(archive), args.output, args.files)

    except CustomError as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
