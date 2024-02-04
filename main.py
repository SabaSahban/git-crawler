import argparse
import logging
from process_repository import process_repositories

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    # parser = argparse.ArgumentParser(description='Process some repositories.')
    # parser.add_argument('--input_file', type=str, help='Path to the input file containing repository URLs',
    #                     required=True)
    # parser.add_argument('--keywords', nargs='+', help='Keywords to search for in commit messages', required=True)
    #
    # args = parser.parse_args()
    # process_repositories(args.input_file, args.keywords)

    input_file = 'repositories.txt'
    keywords = ['feat', 'create']
    process_repositories(input_file, keywords)


if __name__ == "__main__":
    main()
