import sys
import asyncio
from sqlalchemy import inspect

# Añadir el directorio raíz al path
sys.path.append('.')

async def test_create_tables():
    # Importar después de añadir el path
    from app.core.database import engine
    from app.models.user import User
    from sqlmodel import SQLModel
    
    print("------------------------CONECTANDO A LA BASE DE DATOS------------------------")
    
    # Crear todas las tablas
    print("------------------------Creando tablas------------------------")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    print("¡¡¡Tablas creadas exitosamente!!!")
    
    # Verificar que la tabla existe
    print("------------------------Verificando tablas creadas...------------------------")
    async with engine.connect() as conn:
        #función interna síncrona para el inspector
        def inspect_db(sync_conn):
            ins = inspect(sync_conn)
            return {
                "tables": ins.get_table_names(),
                "columns": ins.get_columns('users')
            }

        # Ejecutar la inspección
        results = await conn.run_sync(inspect_db)
        tables = results["tables"]
        columns = results["columns"]
        
        print(f"_____________Tablas en la base de datos: {tables}")
        
        if 'users' in tables:
            print("------------------------Tabla 'users' detectada!------------------------")
            
            # Verificar algunas columnas
            print(f"\n ------------------------Muestra de columnas en 'users':------------------------")
            for col in columns[:5]: 
                print(f"  - {col['name']} ({col['type']})")
            
            # Verificar si tiene las columnas esperadas
            column_names = [col['name'] for col in columns]
            expected_columns = ['id', 'username', 'email', 'is_active']
            for col in expected_columns:
                status = "OK" if col in column_names else "ERROR"
                print(f"  {status} {col}: {'Presente' if col in column_names else 'Ausente'}")
        else:
            print("------------------------La tabla 'users' NO se encontró------------------------")

if __name__ == "__main__":
    asyncio.run(test_create_tables()) 