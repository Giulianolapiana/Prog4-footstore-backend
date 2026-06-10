from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.auth.dependencies import require_roles
from app.modules.images.service import ImageService
from app.modules.images.schemas import ImagePublic

router = APIRouter(prefix="/images", tags=["Images Management"])

def get_image_service(session: Session = Depends(get_session)) -> ImageService:
    return ImageService(session)

@router.get("", response_model=list[ImagePublic])
def list_images(svc: ImageService = Depends(get_image_service)):
    return svc.list_all()

@router.get("/{image_id}", response_model=ImagePublic)
def get_image(image_id: int, svc: ImageService = Depends(get_image_service)):
    return svc.get_by_id(image_id)

@router.post("/upload", response_model=list[ImagePublic], status_code=status.HTTP_201_CREATED)
async def upload_images(
    files: list[UploadFile] = File(...),
    svc: ImageService = Depends(get_image_service),
    _ = Depends(require_roles("ADMIN", "STOCK"))
):
    return await svc.upload_many(files)

@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    image_id: int, 
    svc: ImageService = Depends(get_image_service),
    _ = Depends(require_roles("ADMIN", "STOCK"))
):
    svc.delete(image_id)