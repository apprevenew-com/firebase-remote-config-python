class ValidationError(Exception):
    pass


class VersionMismatchError(Exception):
    pass


class UnexpectedError(Exception):
    pass


class ConditionAlreadyExistsError(Exception):
    pass


class ConditionNotFoundError(Exception):
    pass


class ParameterAlreadyExistsError(Exception):
    pass

class ParameterNotFoundError(Exception):
    pass


class ConditionalValueAlreadySetError(Exception):
    pass
