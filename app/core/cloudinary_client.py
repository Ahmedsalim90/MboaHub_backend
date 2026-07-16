from dataclasses import dataclass
from typing import BinaryIO, Protocol


@dataclass(frozen=True)
class UploadedAsset:
    secure_url: str
    public_id: str


class CloudinaryUploader(Protocol):
    async def upload_image(self, file: BinaryIO, folder: str) -> UploadedAsset: ...


class DisabledCloudinaryClient:
    async def upload_image(self, file: BinaryIO, folder: str) -> UploadedAsset:
        raise RuntimeError("Cloudinary is not configured for this environment")


cloudinary_client: CloudinaryUploader = DisabledCloudinaryClient()
