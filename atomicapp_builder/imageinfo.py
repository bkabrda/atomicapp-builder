class ImageInfo(object):
    """Represents a single image, either an atomicapp meta or binary image."""
    def __init__(self, imagename, vcs_url, vcs_type='git', vcs_local_path=None,
                 vcs_image_buildfile='Dockerfile', image_type='docker', is_meta=False,
                 buildconfigs=None, built=False):
        self.imagename = imagename
        self.vcs_url = vcs_url
        self.vcs_type = vcs_type
        self.vcs_local_path = vcs_local_path
        self.vcs_image_buildfile = vcs_image_buildfile
        self.image_type = image_type
        self.is_meta = is_meta
        self.buildconfigs = buildconfigs
        self.built = False
        self.build_result = None

    def name_str(self, *args, **kwargs):
        return self.imagename.to_str(*args, **kwargs)
