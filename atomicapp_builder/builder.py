import dock

class Builder(object):
    def __init__(self, build_image, df_path, image_name, tag):
        self.build_image = build_image
        self.df_path = df_path
        self.image_name = image_name
        self.tag = tag

    def build(self, wait=True, stream=True):
        response = dock.build_image_using_hosts_docker(
            self.build_image,
            {'provider': 'path', 'uri': 'file://' + self.df_path},
            image=self.tag,
        )
        
        # TODO: handle "wait" and "stream" if requested
        return response
