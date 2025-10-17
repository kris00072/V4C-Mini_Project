import pytest

import employee_manager as em


def test_validate_name():
    assert em.validate_name("Alice") is True
    assert em.validate_name("") is False
    assert em.validate_name("Alice1") is False


def test_validate_hire_date():
    assert em.validate_hire_date("2024-01-01") is True
    assert em.validate_hire_date("01-01-2024") is False


class DummyConn:
    def __init__(self, emails):
        self._emails = set(emails)
    def cursor(self):
        return self
    def execute(self, q, p):
        self._param = p[0]
    def fetchone(self):
        return (1,) if self._param in self._emails else None


def test_validate_email_unique_and_format():
    conn = DummyConn(["taken@example.com"])
    assert em.validate_email("new@example.com", conn) is True
    assert em.validate_email("taken@example.com", conn) is False
    assert em.validate_email("bademail", conn) is False


def test_validate_department():
    assert em.validate_department("Engineering") is True
    assert em.validate_department("") is False


