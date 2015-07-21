class AtomicappBuilderException(Exception):
    def __init__(self, cause):
        super(AtomicappBuilderException, self).__init__(cause)
        self.cause = cause

    def to_str(self):
        ret = str(self.cause)
        if hasattr(self.cause, 'output'):
            ret += ' Subprocess output: {0}'.format(self.cause.output)
        return ret
