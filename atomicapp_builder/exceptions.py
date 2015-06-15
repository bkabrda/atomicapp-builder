class AtomicappBuilderException(Exception):
    def __init__(self, cause):
        super(AtomicappBuilderException, self).__init__(cause)
        self.cause = cause

    def to_str(self):
        return str(self.cause)
