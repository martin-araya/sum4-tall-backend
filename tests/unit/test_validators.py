import pytest
from app.utils.validators import validate_email_format, validate_phone, validate_rut


@pytest.mark.parametrize(
    "rut,expected",
    [
        ("19.000.001-K", True),
        ("19000001K", True),
        ("19000001-k", True),
        ("12.345.678-5", True),
        ("12345678-5", True),
        ("12.345.678-K", False),  # DV incorrecto
        ("123", False),  # Formato incorrecto
        ("invalid-rut", False),
    ],
)
def test_validate_rut(rut: str, expected: bool) -> None:
    assert validate_rut(rut) == expected


@pytest.mark.parametrize(
    "phone,expected",
    [
        ("+56912345678", True),
        ("912345678", True),
        ("+56 9 1234 5678", True),
        ("+12345678901", True),
        ("invalid-phone", False),
        ("12345", False),
    ],
)
def test_validate_phone(phone: str, expected: bool) -> None:
    assert validate_phone(phone) == expected


@pytest.mark.parametrize(
    "email,expected",
    [
        ("test@example.com", True),
        ("user.name+tag@domain.co.uk", True),
        ("invalid-email", False),
        ("test@domain", False),
        ("@domain.com", False),
    ],
)
def test_validate_email_format(email: str, expected: bool) -> None:
    assert validate_email_format(email) == expected
