import argparse
import tempfile
import sys

from atomicapp_builder import builder
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
        '--build-image',
        dest='build_image',
        help='Name of image that Dock should use to build images (defaults to "buildroot")',
        default='buildroot')
    build_sp.add_argument(
        '--tag',
        dest='tag',
        help='Tag for the resulting image (app id will be used if tag is not provided)',
        default=None)
    build_sp.add_argument(
        '-q', '--quiet',
        dest='quiet',
        help='Only output names of built images after build is done',
        action='store_true',
        default=False)
    build_sp.add_argument(
        'what',
        metavar='PATH | cccp:<app-id>',
        help='Path to directory with Nulecule file to build or app id prefixed by "cccp:"')

    return parser


def build(args):
    tmpdir = tempfile.mkdtemp()
    to_build = resolver.Resolver(args['what'], args['cccp_index'], tmpdir).resolve()

    build_results = {}
    # we build one by one, since builder is not thread safe (because dock is not)
    for image_name, df_path in to_build.items():
        bldr = builder.Builder(args['build_image'], df_path, image_name, args['tag'])
        build_results[image_name] = bldr.build(wait=True, stream=not args['quiet'])

    failed = []
    succeeded = []
    for image, result in build_results.items():
        if result.return_code != 0:
            failed.append(image)
        else:
            succeeded.append(image)

    if succeeded:
        if not args['quiet']:
            print('Images built successfully:')
        print('\n'.join(succeeded))
    for f in failed:
        print('Failed to build image {0}'.format(f))
    return len(failed)


def run():
    parser = create_parser()
    args = vars(parser.parse_args())
    if args['action'] == 'build':
        try:
            result = build(args)
        except Exception as e:
            result = 1
            print(e)
        sys.exit(result)
