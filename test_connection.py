import asyncio
from app.core.database import engine
from sqlalchemy import text

async def test_connection():
    """
    Función asíncrona para probar la conexión a la base de datos.
    """
    try:
        # Usar async with para conexiones asíncronas
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            print("Conexión exitosa a la base de datos")
            print(f"Resultado: {result.fetchone()}")
        
        # También se puede probar create_db_and_tables si se desea crear tablas
        # from app.core.database import create_db_and_tables
        # await create_db_and_tables()
        # print(" Tablas creadas exitosamente")
        
    except Exception as e:
        print(f"Error de conexión: {e}")

    finally: # Cerrar el engine al finalizar (si se borran 25 y 26 se queda abierta la conexión)
        await engine.dispose()

if __name__ == "__main__":
    # Ejecutar la función asíncrona
    asyncio.run(test_connection())