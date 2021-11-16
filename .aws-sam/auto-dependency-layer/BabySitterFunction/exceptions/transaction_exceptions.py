class TransactWriteException(Exception):
    def __init__(self, errorObj):
        super(TransactWriteException, self).__init__()

        self.details = errorObj
