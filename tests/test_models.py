import sys
import asyncio
from sqlalchemy import inspect, text
from sqlmodel import SQLModel

# Añadir el directorio raíz al path para permitir importaciones locales
sys.path.append('.')

async def test_create_tables():
    # Importaciones diferidas para asegurar que el path esté configurado
    from app.core.database import engine
    from app.models.user import User  # Asegura que el modelo esté cargado en SQLModel

    print("\n--- INICIANDO REVISIÓN DE MODELOS EN POSTGRESQL ---")
    
    # 1. Crear las tablas en el contenedor de Docker
    print("Sincronizando metadatos (tablas) con la base de datos...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("¡Tablas creadas o verificadas exitosamente!")

    # 2. Inspeccionar la estructura de la base de datos
    print("\n--- VERIFICANDO ESTRUCTURA DE COLUMNAS ---")
    async with engine.connect() as conn:
        # Función interna para ejecutar el inspector sincrónico de SQLAlchemy
        def inspect_db(sync_conn):
            ins = inspect(sync_conn)
            return {
                "tables": ins.get_table_names(),
                "columns": ins.get_columns('users')
            }

        # Ejecutar la inspección de forma sincronizada con el hilo asíncrono
        results = await conn.run_sync(inspect_db)
        
        tables = results["tables"]
        columns = results["columns"]

        print(f"\nTablas detectadas: {tables}")

        if 'users' in tables:
            print("\n[OK] Tabla 'users' detectada correctamente.")
            print("Muestra de columnas y tipos nativos en PostgreSQL:")
            
            # Verificar las primeras 8 columnas relevantes
            for col in columns[:8]:
                print(f" -> Columna: {col['name']} | Tipo: {col['type']}")

            # Validación de columnas críticas para la API
            column_names = [col['name'] for col in columns]
            expected_columns = ['id', 'username', 'email', 'is_active', 'created_at']
            
            print("\nChequeo de integridad:")
            for col in expected_columns:
                status = "PASS" if col in column_names else "FAIL"
                print(f" [{status}] {col}")
        else:
            print("\n[ERROR] La tabla 'users' no se encontró en la base de datos.")

    # Cerrar el pool de conexiones
    await engine.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(test_create_tables())
    except KeyboardInterrupt:
        pass

