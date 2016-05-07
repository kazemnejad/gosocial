class AuthExceptions:
    class UserExistException(Exception):
        pass

    class FailedRegistration(Exception):
        pass

    class InvalidCredentialsException(Exception):
        pass
