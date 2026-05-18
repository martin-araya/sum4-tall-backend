import asyncio
import os
import asyncpg
from app.core.config import get_settings

async def main():
    settings = get_settings()
    db_url = settings.database_url
    
    # asyncpg.connect requires standard postgresql:// or postgres://, not postgresql+asyncpg://
    if "postgresql+asyncpg://" in db_url:
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    
    # Mask password in log output
    masked_url = db_url
    try:
        if "@" in db_url:
            parts = db_url.split("@")
            creds = parts[0].split(":")
            if len(creds) > 2:
                masked_url = f"{creds[0]}:{creds[1]}:******@{parts[1]}"
    except Exception:
        pass

    print(f"Conectando a la base de datos: {masked_url}")
    
    try:
        conn = await asyncpg.connect(db_url)
        print("¡Conexión establecida con éxito!")
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        print("\nPor favor, verifica que hayas actualizado tu contraseña en el archivo .env")
        return

    # Leer init.sql
    print("Leyendo init.sql...")
    try:
        with open("init.sql", "r", encoding="utf-8") as f:
            init_sql = f.read()
    except Exception as e:
        print(f"Error al leer init.sql: {e}")
        await conn.close()
        return

    # Leer seed.sql
    print("Leyendo seed.sql...")
    try:
        with open("seed.sql", "r", encoding="utf-8") as f:
            seed_sql = f.read()
    except Exception as e:
        print(f"Error al leer seed.sql: {e}")
        await conn.close()
        return

    try:
        print("Ejecutando init.sql (creando esquema, extensiones, tipos y tablas)...")
        await conn.execute(init_sql)
        print("¡Esquema y tablas creados correctamente!")

        print("Ejecutando seed.sql (insertando datos de semilla)...")
        await conn.execute(seed_sql)
        print("¡Datos de prueba insertados correctamente!")
        
    except Exception as e:
        print(f"Error durante la ejecución de los scripts SQL: {e}")
    finally:
        await conn.close()
        print("Conexión cerrada.")

if __name__ == "__main__":
    asyncio.run(main())
