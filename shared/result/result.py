from typing import Generic, TypeVar, Optional

T = TypeVar("T")
E = TypeVar("E", bound=str)

class Result(Generic[T, E]):
    def __init__(self, is_success: bool, value: Optional[T] = None, error: Optional[E] = None):
        self._is_success = is_success
        self._value = value
        self._error = error

    @property
    def is_success(self) -> bool:
        return self._is_success

    @property
    def is_failure(self) -> bool:
        return not self._is_success

    @property
    def value(self) -> T:
        if not self._is_success:
            raise ValueError(f"Cannot access value of a failed result. Error was: {self._error}")
        return self._value  # type: ignore

    @property
    def error(self) -> E:
        if self._is_success:
            raise ValueError("Cannot access error of a successful result.")
        return self._error  # type: ignore

    @classmethod
    def success(cls, value: Optional[T] = None) -> "Result[T, E]":
        return cls(is_success=True, value=value)

    @classmethod
    def failure(cls, error: E) -> "Result[T, E]":
        return cls(is_success=False, error=error)

    def __repr__(self) -> str:
        if self._is_success:
            return f"Success({self._value})"
        return f"Failure({self._error})"