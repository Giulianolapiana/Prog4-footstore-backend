import asyncio
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status
from sqlmodel import Session

from app.modules.images.models import ImageEntity
from app.modules.images.schemas import ImagePublic
from app.modules.images.unit_of_work import ImageUnitOfWork

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024

class ImageService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[ImagePublic]:
        with ImageUnitOfWork(self._session) as uow:
            images = uow.images.get_all_ordered()
            return [ImagePublic.model_validate(img) for img in images]

    def get_by_id(self, image_id: int) -> ImagePublic:
        with ImageUnitOfWork(self._session) as uow:
            image = uow.images.get_by_id(image_id)
            if not image:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagen no encontrada")
            return ImagePublic.model_validate(image)

    async def upload_many(self, files: list[UploadFile]) -> list[ImagePublic]:
        results: list[ImagePublic] = []
        
        for file in files:
            if file.content_type not in ALLOWED_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Archivo '{file.filename}' no soportado. Usa JPG, PNG o WEBP.",
                )
            
            content = await file.read()
            
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"El archivo '{file.filename}' excede el límite de 5 MB.",
                )
            
            try:

                upload_result = await asyncio.to_thread(
                    cloudinary.uploader.upload,
                    content,
                    folder="foodstore/productos",
                    resource_type="image",
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error subiendo a la nube: {str(e)}"
                )

            with ImageUnitOfWork(self._session) as uow:
                image_entity = ImageEntity(
                    public_id=upload_result["public_id"],
                    url=upload_result["secure_url"],
                    filename=file.filename or upload_result["public_id"],
                    format=upload_result.get("format"),
                    width=upload_result.get("width"),
                    height=upload_result.get("height"),
                    bytes=upload_result.get("bytes"),
                )
                saved = uow.images.add(image_entity)
                uow._session.flush() 
                results.append(ImagePublic.model_validate(saved))
                
        return results

    def delete(self, image_id: int) -> None:
        with ImageUnitOfWork(self._session) as uow:
            image = uow.images.get_by_id(image_id)
            if not image:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagen no encontrada")
            
            try:
                cloudinary.uploader.destroy(image.public_id, resource_type="image")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                    detail=f"Error borrando de la nube: {str(e)}"
                )
                
            uow.images.delete(image)