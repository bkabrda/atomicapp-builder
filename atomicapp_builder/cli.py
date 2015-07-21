import argparse
import logging
import tempfile
import sys

import atomicapp_builder
from atomicapp_builder.builder import Builder
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
        help='Name of image that Dock should use to build images (defaults to "atomic-reactor")',
        default='atomic-reactor')
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
    # first resolve the images that were already built and that we'll need to build
    # TODO: remove tmpdir when done
    tmpdir = tempfile.mkdtemp()
    apps = resolver.Resolver(
        args['what'],
        args['cccp_index'],
        args['docker_registry'],
        args['registry_insecure'],
        tmpdir).resolve()

    func_result = 0
    for a in apps:
        if a.meta_image.built:
            logger.info('Meta image for app "{0}" already built.'.format(a.appid))
        else:
            doing_what = 'Building'
            if args['docker_registry']:
                doing_what += 'and pushing'
            logger.info('{doing} meta image "{mi}" for app "{app}" ...'.
                        format(doing=doing_what, mi=a.meta_image.imagename, app=a.appid))
            bldr = Builder(
                args['build_image'],
                a.meta_image,
                registry=args['docker_registry'],
                registry_insecure=args['registry_insecure'],
            )
            res = bldr.build()
            if not res:
                func_result = 1
            for l in a.meta_image.build_result.build_logs:
                logger.debug(l)
            logger.info('{doing} meta image "{mi}" for app "{app}" {result}.'.
                        format(doing=doing_what, mi=a.meta_image.imagename, app=a.appid,
                               result='succeeded' if res else 'failed')
                        )

    return func_result


def run():
    parser = create_parser()
    args = vars(parser.parse_args())
    if args['log_level'] is None:
        # TODO: seems that when set_defaults is used on the top level parser directly,
        #  then then it doesn't propagate to supbarsers; so just check it here
        args['log_level'] = logging.INFO
    atomicapp_builder.set_logging(args['log_level'])
    logger.debug('atomicapp-builder invoked:')
    logger.debug('%s', ' '.join(sys.argv))

    if args['action'] == 'build':
        result = 1
        try:
            result = build(args)
        except exceptions.AtomicappBuilderException as e:
            logger.error(e.to_str())
        except Exception as e:
            logger.exception('Exception while running %s:', sys.argv[0])
        sys.exit(result)
