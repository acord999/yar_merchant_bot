class ClientAlreadyExistError(Exception):
    """"User currently exist"""


class NoSuchClientError(Exception):
    """No such client exist"""


class NoSuchCategoryError(Exception):
    """No such category exist"""


class NoSuchProductError(Exception):
    """No such product exist"""