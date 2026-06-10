# lo ponemos globalmente, para que no se cargue cada vez que usamos el service de images
import cloudinary
from app.core.config import settings

def init_cloudinary() -> None:
    """Inicializa la configuración global de Cloudinary al arrancar la app."""
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )