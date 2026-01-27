import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Añadir el path raíz para importar módulos
sys.path.append('.')

async def create_data():
    from app.core.database import engine
    from app.models.user import User
    from app.core.security import get_password_hash
    from sqlmodel import select

    # Configurar la sesión asíncrona para la base de datos
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    print("--------------------Iniciando creación de usuario...--------------------")

    async with async_session() as session:
        # Verifica si el usuario ya existe
        statement = select(User).where(User.username == "Lore")
        result = await session.execute(statement)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"--------------------El usuario '{existing_user.username}' ya existe.--------------------")
            return

        #Crea nuevo usuario con contraseña hasheada
        new_user = User(
            username="Lore",
            email="lore@example.com",
            password=get_password_hash("admin123"), # ¡Hash, no texto plano!
            first_name="Lorena",
            last_name="Martinez",
            is_superuser=True,
            is_active=True
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        print(f" --------------------Usuario creado exitosamente: --------------------")
        print(f"   ID (UUID): {new_user.id}")
        print(f"   Username: {new_user.username}")
        print(f"   Password en DB (Hash): {new_user.password[:20]}...")
        print(f"   Email: {new_user.email}")
        print(f"   Creado en: {new_user.created_at}")
        print(f"   Nombre completo: {getattr(new_user, 'full_name', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(create_data()) 