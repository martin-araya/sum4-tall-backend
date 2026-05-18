from app.core.security import get_password_hash, verify_password


def test_argon2id_password_hashing() -> None:
    password = "secret_password"
    hashed = get_password_hash(password)

    # El hash de Argon2id comienza con $argon2id$
    assert hashed.startswith("$argon2id$")

    # Verificar que el password sea correcto
    assert verify_password(password, hashed) is True

    # Verificar que un password incorrecto falle
    assert verify_password("wrong_password", hashed) is False


def test_bcrypt_legacy_fallback() -> None:
    # Hash bcrypt generado por la herramienta passlib heredada para la clave "admin123"
    legacy_hash = "$2b$12$58h7Wjzll72ddUGtHWvRFeqlclV/iy/yPVNv1EFh0Wi/0BN3UY/jC"

    # Verificar que verify_password funciona correctamente con hashes heredados de bcrypt
    assert verify_password("admin123", legacy_hash) is True
    assert verify_password("wrong_password", legacy_hash) is False
