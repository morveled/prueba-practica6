import asyncio
from app.core.database import engine
from sqlalchemy import text

async def test_connection():
    """
    Función asíncrona para validar la conectividad con el contenedor de PostgreSQL.
    Realiza una consulta simple (SELECT 1) para confirmar que el servicio responde.
    """
    print("Iniciando prueba de conexión con PostgreSQL...")
    try:
        # Se establece la conexión asíncrona utilizando el engine configurado
        async with engine.connect() as connection:
            # Se ejecuta una consulta de validación
            result = await connection.execute(text("SELECT 1"))
            row = result.fetchone()
            
            if row:
                print("------------------------------------------")
                print("¡Conexión exitosa a la base de datos!")
                print(f"Resultado de la consulta de prueba: {row[0]}")
                print("------------------------------------------")
            
    except Exception as e:
        print("------------------------------------------")
        print(f"Error de conexión: {e}")
        print("Asegúrese de que el contenedor de Docker esté en ejecución.")
        print("------------------------------------------")
    finally:
        # Se libera el pool de conexiones del engine
        await engine.dispose()

if __name__ == "__main__":
    # Ejecución del bucle de eventos de asyncio
    asyncio.run(test_connection())

