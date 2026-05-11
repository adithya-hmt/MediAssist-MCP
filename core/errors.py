"""Shared exceptions for predictable tool failures."""

from __future__ import annotations


class MediAssistError(Exception):
    """Base error for the project."""


class InputValidationError(MediAssistError):
    """Raised when a tool input cannot be processed safely."""


class DataNotFoundError(MediAssistError):
    """Raised when synthetic data does not contain a requested lookup."""

