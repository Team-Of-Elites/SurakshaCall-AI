class DatabaseError(Exception):
    pass

class DatabaseUnavailableError(DatabaseError):
    pass

class DatabaseLockedError(DatabaseError):
    pass

class DatabaseConstraintError(DatabaseError):
    pass

class DatabaseCorruptionError(DatabaseError):
    pass

class PrivacyViolationError(DatabaseError):
    pass

class SerializationError(DatabaseError):
    pass
