"""Repository protocol definitions for dependency inversion."""

from api.repositories.account import AccountRepositoryProtocol
from api.repositories.case import CaseRepositoryProtocol
from api.repositories.document import DocumentRepositoryProtocol
from api.repositories.task import TaskRepositoryProtocol
from api.repositories.user import UserRepositoryProtocol

__all__ = [
    "AccountRepositoryProtocol",
    "CaseRepositoryProtocol",
    "DocumentRepositoryProtocol",
    "TaskRepositoryProtocol",
    "UserRepositoryProtocol",
]
