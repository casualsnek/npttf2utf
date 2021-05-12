# Font Mapper exceptions
class NoMapForOriginException(Exception):
    pass


# General file type handler exceptions
class UnsupportedMapToException(Exception):
    pass


# Txt File handler exceptions
class TxtAutoModeException(Exception):
    pass


# Exception for when map file is not found
class MapFileNotFoundException(Exception):
    pass
