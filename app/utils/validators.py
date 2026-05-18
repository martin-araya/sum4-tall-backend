import re


def validate_rut(rut: str) -> bool:
    """Valida un RUT chileno (con o sin puntos y guión)."""
    # Eliminar espacios, puntos y guiones
    rut = rut.replace(".", "").replace("-", "").upper().strip()
    if not re.match(r"^\d{7,8}[0-9K]$", rut):
        return False

    rut_digits = rut[:-1]
    dv = rut[-1]

    # Calcular dígito verificador usando algoritmo módulo 11
    suma = 0
    multiplo = 2
    for d in reversed(rut_digits):
        suma += int(d) * multiplo
        multiplo = 2 if multiplo == 7 else multiplo + 1

    res = 11 - (suma % 11)
    if res == 11:
        expected_dv = "0"
    elif res == 10:
        expected_dv = "K"
    else:
        expected_dv = str(res)

    return dv == expected_dv


def validate_phone(phone: str) -> bool:
    """Valida un número telefónico (formato internacional o nacional chileno)."""
    # Ejemplos válidos: +56912345678, 912345678, +123456789
    clean_phone = phone.replace(" ", "").strip()
    return bool(
        re.match(r"^(\+?56)?9[0-9]{8}$", clean_phone)
        or re.match(r"^\+[1-9]\d{1,14}$", clean_phone)
    )


def validate_email_format(email: str) -> bool:
    """Valida un formato de correo electrónico básico."""
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))
