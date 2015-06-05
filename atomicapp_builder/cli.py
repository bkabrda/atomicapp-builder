import argparse
import tempfile
import sys

from atomicapp_builder import constants
from atomicapp_builder import resolver


def create_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')
    build_sp = subparsers.add_parser('build')

    build_sp.add_argument(
        '--cccp-index',
        dest='cccp_index',
        help='URI of raw cccp index file (can be file:// for local file)',
        default=constants.DEFAULT_CCCP_INDEX)
    build_sp.add_argument(
        'what',
        metavar='PATH | cccp:<app-id>',
        help='Path to directory with Nulecule file to build or app id prefixed by "cccp:"')

    return parser


def build(args):
    tmpdir = tempfile.mkdtemp()
    images_to_build = resolver.Resolver(args['what'], args['cccp_index'], tmpdir).resolve()
    print(images_to_build)


def run():
    parser = create_parser()
    args = vars(parser.parse_args())
    if args['action'] == 'build':
        try:
            result = build(args)
        except Exception as e:
            print(e)
            sys.exit(1)
        else:
            sys.exit(0)
