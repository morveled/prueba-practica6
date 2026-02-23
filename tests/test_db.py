import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select

# Se añade el path raíz para permitir la importación de módulos locales
sys.path.append('.')

async def create_data_test():
    # Importaciones diferidas para asegurar la carga correcta del entorno
    from app.core.database import engine
    from app.models.user import User
    from app.core.security import get_password_hash

    # Se configura la fábrica de sesiones asíncronas para la prueba
    async_session = sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )

    print("\n--- INICIANDO PRUEBA DE CREACIÓN DE USUARIO EN POSTGRESQL ---")

    async with async_session() as session:
        # 1. Se verifica si el usuario ya existe en la BD
        test_username = "Lore"
        statement = select(User).where(User.username == test_username)
        result = await session.execute(statement)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"El usuario '{test_username}' ya existe en la base de datos.")
            user_to_show = existing_user
        else:
            # 2. Creación de un nuevo usuario con contraseña hasheada
            print(f"Creando nuevo usuario: {test_username}...")
            new_user = User(
                username=test_username,
                email="lore@example.com",
                password=get_password_hash("admin123"), # Se aplica el hash seguro
                first_name="Lorena",
                last_name="Martinez",
                is_superuser=True,
                is_active=True
            )
            
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            user_to_show = new_user
            print("¡Usuario creado exitosamente!")

        # 3. Validación de datos y propiedades calculadas
        print("\n--- RESUMEN DEL REGISTRO ---")
        print(f"ID (UUID):       {user_to_show.id}")
        print(f"Username:        {user_to_show.username}")
        print(f"Email:           {user_to_show.email}")
        print(f"Password Hash:   {user_to_show.password[:20]}...")
        print(f"Nombre Completo: {user_to_show.full_name}") # Propiedad del modelo
        print(f"Fecha Registro:  {user_to_show.date_joined}")
        
        if user_to_show.age:
            print(f"Edad calculada:  {user_to_show.age}")

    # Cierre del pool de conexiones
    await engine.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(create_data_test())
    except KeyboardInterrupt:
        pass

