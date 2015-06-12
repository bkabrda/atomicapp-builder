Atomicapp Builder
=================

An application to build application images from [Nulecule](https://github.com/projectatomic/nulecule).

Usage:

```
atomicapp-builder build [-h] [--cccp-index CCCP_INDEX]
                             [--build-image BUILD_IMAGE]
                             [--docker-registry DOCKER_REGISTRY]
                             [--registry-insecure] [-q | -v]
                             PATH | cccp:<app-id>

positional arguments:
  PATH | cccp:<app-id>  Path to directory with Nulecule file to build or app id prefixed by "cccp:"

optional arguments:
  -h, --help            show this help message and exit
  --cccp-index CCCP_INDEX
                        URI of raw cccp index file (can be file:// for local file), defaults to
                        https://raw.githubusercontent.com/kbsingh/cccp-index/master/index.yml
  --build-image BUILD_IMAGE
                        Name of image that Dock should use to build images (defaults to "buildroot")
  --docker-registry DOCKER_REGISTRY
                        URL of Docker registry to poll for existing images and
                        push built images to. Must be without http/https
                        scheme.
  --registry-insecure   If used, plain http will be used to connect to
                        registry instead of https
  -q, --quiet           Only output names of built images after build is done
  -v, --verbose         Print lots of debugging information
```

Requires `anymarkup`, `requests` and `dock`. You can get the first two just by typing
`pip install --user -r requirements.txt` and you can get `dock` from
https://github.com/DBuildService/dock. This also requires `dock`'s build image. You
can either get one by `docker pull slavek/buildroot` or build one yourself.
