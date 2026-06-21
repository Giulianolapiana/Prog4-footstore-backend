import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
import io
from app.modules.uploads.models import ImageEntity
from sqlmodel import Session

def test_subir_imagen(client: TestClient, admin_cookies: dict):
    fake_file = io.BytesIO(b"fake image data")
    fake_file.name = "test.png"
    
    with patch("app.modules.uploads.service.cloudinary.uploader.upload") as mock_upload:
        mock_upload.return_value = {
            "secure_url": "https://res.cloudinary.com/demo/image/upload/v1234/test.png",
            "public_id": "test_id",
            "width": 800,
            "height": 600,
            "format": "png",
            "resource_type": "image"
        }
        
        res = client.post(
            "/api/v1/uploads/upload",
            files={"files": ("test.png", fake_file, "image/png")},
            cookies=admin_cookies
        )
        assert res.status_code == 201

def test_eliminar_imagen(client: TestClient, admin_cookies: dict, db_session: Session):
    img = ImageEntity(
        public_id="test_id_to_delete",
        url="http://test.url",
        filename="test.png",
        format="png",
        width=100,
        height=100
    )
    db_session.add(img)
    db_session.commit()
    db_session.refresh(img)

    with patch("app.modules.uploads.service.cloudinary.uploader.destroy") as mock_destroy:
        mock_destroy.return_value = {"result": "ok"}
        
        res = client.delete(
            f"/api/v1/uploads/{img.id}",
            cookies=admin_cookies
        )
        assert res.status_code == 204
