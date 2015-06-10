import argparse
import logging
import tempfile
import sys

import atomicapp_builder
from atomicapp_builder import builder
from atomicapp_builder import constants
from atomicapp_builder import resolver

logger = logging.getLogger(__name__)


def create_parser():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='action')
    build_sp = subparsers.add_parser('build')

    build_sp.add_argument(
        '--cccp-index',
        dest='cccp_index',
        help='URI of raw cccp index file (can be file:// for local file), defaults to '
        'https://raw.githubusercontent.com/kbsingh/cccp-index/master/index.yml',
        default=constants.DEFAULT_CCCP_INDEX)
    build_sp.add_argument(
        '--build-image',
        dest='build_image',
        help='Name of image that Dock should use to build images (defaults to "buildroot")',
        default='buildroot')
    # TODO: we would need to be able to specify tags for all built images,
    #  so we'll have to think of something smarter than just one tag, probably
    # build_sp.add_argument(
    #    '--tag',
    #    dest='tag',
    #    help='Tag for the resulting image (app id will be used if tag is not provided)',
    #    default=None)
    log_level_ag = build_sp.add_mutually_exclusive_group()
    log_level_ag.add_argument(
        '-q', '--quiet',
        dest='log_level',
        help='Only output names of built images after build is done',
        action='store_const',
        const=logging.ERROR)
    log_level_ag.add_argument(
        '-v', '--verbose',
        dest='log_level',
        help='Print lots of debugging information',
        action='store_const',
        const=logging.DEBUG)
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
        bldr = builder.Builder(args['build_image'], df_path, image_name) #  , args['tag'])
        build_results[image_name] = bldr.build(wait=True, log_level=args['log_level'])

    failed = []
    succeeded = []
    for image, result in build_results.items():
        if result.return_code != 0:
            failed.append(image)
        else:
            succeeded.append(image)

    if succeeded:
        logging.info('Images built successfully:')
        print('\n'.join(succeeded))
    for f in failed:
        print('Failed to build image {0}'.format(f))
    return len(failed)


def run():
    parser = create_parser()
    args = vars(parser.parse_args())
    if args['log_level'] is None:
        # TODO: seems that when set_defaults is used on the top level parser directly,
        #  then then it doesn't propagate to supbarsers; so just check it here
        args['log_level'] = logging.INFO
    atomicapp_builder.set_logging(args['log_level'])

    if args['action'] == 'build':
        try:
            result = build(args)
        except Exception as e:
            result = 1
            logger.exception('Exception while running {0}:'.format(sys.argv[0]))
        sys.exit(result)
