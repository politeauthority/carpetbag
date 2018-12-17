"""Errors
CarpetBag Errors that might be thrown when problems happen
"""


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class EmptyProxyBag(Error):
    """Raised when the input value is too small"""
    pass


class InvalidContinent(Error):
    """Raised when an unknwon continent is supplied by the user"""
    pass


class NoRemoteServicesConnection(Error):
    """Raised when CarpetBag cannot talk to bad-actor.services"""
    pass


class CannotOverwriteFile(Error):
    """Raised when trying to download a file to a local location that already has a file"""
    pass

# EndFile: carpetbag/carpetbag/errors.py
