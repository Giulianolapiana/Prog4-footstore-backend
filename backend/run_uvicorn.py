import uvicorn
import os
from dotenv import load_dotenv

def main():
    """
    Script de inicio para la aplicación FastAPI.
    Detecta automáticamente el entorno y configura uvicorn en consecuencia.
    """
    # Cargar variables de entorno desde el archivo .env
    load_dotenv()

    # Detectar configuraciones (con valores por defecto seguros para desarrollo local)
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Activar el modo 'reload' solo si estamos en entorno de desarrollo
    # Esto es crucial para la experiencia de desarrollo en VS Code
    is_development = environment.lower() == "development"

    print("====================================================================")
    print(f"🚀 Iniciando servidor Uvicorn para FoodStore API")
    print(f"🌍 Entorno: {environment}")
    print(f"📡 Host: {host} | Puerto: {port}")
    print(f"🔄 Auto-Reload: {'Activado' if is_development else 'Desactivado'}")
    print("====================================================================\n")

    # Ejecutar el servidor uvicorn apuntando al módulo 'main' y la instancia 'app'
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=is_development,
        log_level="info",
        use_colors=True,
        # Opcionalmente se puede forzar la implementación de websockets si se requiere, 
        # pero uvicorn lo autodetecta por defecto (websockets o wsproto)
        ws="auto" 
    )

if __name__ == "__main__":
    main()
