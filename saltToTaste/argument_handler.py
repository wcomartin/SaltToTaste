import argparse

def create_parser():
    parser = argparse.ArgumentParser(description='A Flask based recipe platform')
    parser.add_argument('--datadir', help='Specify a directory to store your data files')
    return parser

def parser_results():
    parser = create_parser()
    args = parser.parse_args()
    results = {
        'DATA_DIR' : None
    }

    if args.datadir:
        results['DATA_DIR'] = args.datadir.rstrip('/')
    else:
        results['DATA_DIR'] = "config"

    return results
