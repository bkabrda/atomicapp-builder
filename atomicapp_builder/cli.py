import argparse
import logging
import tempfile
import sys

import atomicapp_builder
from atomicapp_builder import builder
from atomicapp_builder import constants
from atomicapp_builder import exceptions
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
    build_sp.add_argument(
        '--docker-registry',
        dest='docker_registry',
        help='URL of Docker registry to poll for existing images and push built images to. '
             'Must be without http/https scheme.',
        default=None)
    build_sp.add_argument(
        '--registry-insecure',
        dest='registry_insecure',
        help='If used, plain http will be used to connect to registry instead of https',
        action='store_true',
        default=False)
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
    imgs_to_str = lambda imgs: ' '.join([i.repo for i in imgs])

    # first resolve the images that were already built and that we'll need to build
    tmpdir = tempfile.mkdtemp()
    already_built, to_build = resolver.Resolver(
        args['what'],
        args['cccp_index'],
        args['docker_registry'],
        args['registry_insecure'],
        tmpdir).resolve()
    logger.info('Images already built: {0}'.format(imgs_to_str(already_built) or '<None>'))
    logger.info('Images to build: {0}'.format(imgs_to_str(to_build) or '<None>'))

    build_results = {}
    # we build one by one, since builder is not thread safe (because dock is not)
    for image_name, df_path in to_build.items():
        bldr = builder.Builder(
            args['build_image'],
            df_path,
            image_name,
            registry=args['docker_registry'],
            registry_insecure=args['registry_insecure'])
        build_results[image_name] = bldr.build(wait=True, log_level=args['log_level'])

    # found out which ones failed and succeeded and print this info
    failed = []
    succeeded = []
    for image, result in build_results.items():
        # TODO: save build logs from individual builds to a log file for inspection?
        if result.return_code != 0:
            for l in result.build_logs:
                print(l)
            failed.append(image)
        else:
            succeeded.append(image)

    if succeeded:
        if args['docker_registry']:
            logger.info('Images built and pushed successfully:')
        else:
            logger.info('Images built successfully:')
        print(imgs_to_str(succeeded).replace(' ', '\n'))
    for f in failed:
        print('Failed to build image {0}'.format(f.repo))
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
        result = 1
        try:
            result = build(args)
        except exceptions.AtomicappBuilderException as e:
            logger.error(e.to_str())
        except Exception as e:
            logger.exception('Exception while running {0}:'.format(sys.argv[0]))
        sys.exit(result)
