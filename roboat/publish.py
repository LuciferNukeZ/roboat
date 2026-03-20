"""
roboat.publish
~~~~~~~~~~~~~~
Asset publishing and upload via Roblox Open Cloud Assets API.
Upload images, models, audio, and animations directly from Python.

Requires Open Cloud API key with asset upload permission.

Example::

    from roboat.publish import PublishAPI

    pub = PublishAPI(api_key="roblox-KEY-xxxx", creator_id=123, creator_type="User")

    # Upload an image
    asset = pub.upload_image(
        file_path="thumbnail.png",
        name="My Game Thumbnail",
        description="Updated thumbnail",
    )
    print(asset)

    # Upload audio
    asset = pub.upload_audio(
        file_path="bgm.ogg",
        name="Background Music",
    )
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import os
import requests


@dataclass
class UploadedAsset:
    operation_id: str
    asset_id: Optional[int]
    name: str
    asset_type: str
    status: str

    @classmethod
    def from_dict(cls, d: dict) -> "UploadedAsset":
        meta = d.get("assetDetails", d.get("response", {}))
        return cls(
            operation_id=d.get("operationId", d.get("path", "")),
            asset_id=meta.get("assetId"),
            name=meta.get("displayName", ""),
            asset_type=meta.get("assetType", ""),
            status=d.get("done", False) and "Complete" or "Pending",
        )

    def __str__(self) -> str:
        aid = f" [Asset ID: {self.asset_id}]" if self.asset_id else ""
        return f"📦 {self.name} ({self.asset_type}){aid} — {self.status}"


# Supported MIME types per asset type
_MIME_MAP = {
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".bmp":  "image/bmp",
    ".tga":  "image/tga",
    ".ogg":  "audio/ogg",
    ".mp3":  "audio/mpeg",
    ".fbx":  "model/fbx",
}

_TYPE_MAP = {
    ".png":  "Image", ".jpg": "Image", ".jpeg": "Image",
    ".bmp":  "Image", ".tga": "Image",
    ".ogg":  "Audio", ".mp3": "Audio",
    ".fbx":  "Model",
}


class PublishAPI:
    """
    Upload and publish assets via Open Cloud.

    Args:
        api_key: Open Cloud API key.
        creator_id: Your user ID or group ID.
        creator_type: "User" or "Group".
    """

    BASE = "https://apis.roblox.com/assets/v1"

    def __init__(self, api_key: str, creator_id: int,
                 creator_type: str = "User", timeout: int = 30):
        self._key = api_key
        self._creator_id = creator_id
        self._creator_type = creator_type
        self._timeout = timeout

    def _upload(self, file_path: str, name: str,
                description: str, asset_type: str,
                mime_type: str) -> UploadedAsset:
        """Internal upload method."""
        creator_key = "userId" if self._creator_type == "User" else "groupId"
        request_json = {
            "assetType": asset_type,
            "displayName": name,
            "description": description,
            "creationContext": {
                "creator": {creator_key: self._creator_id},
                "expectedPrice": 0,
            },
        }
        with open(file_path, "rb") as f:
            file_data = f.read()

        r = requests.post(
            f"{self.BASE}/assets",
            headers={"x-api-key": self._key},
            data={"request": str(request_json)},
            files={"fileContent": (os.path.basename(file_path), file_data, mime_type)},
            timeout=self._timeout,
        )
        r.raise_for_status()
        return UploadedAsset.from_dict(r.json())

    def upload_image(self, file_path: str, name: str,
                     description: str = "") -> UploadedAsset:
        """
        Upload an image asset (PNG, JPG, BMP, TGA).

        Args:
            file_path: Path to the image file.
            name: Display name for the asset.
            description: Optional description.

        Returns:
            UploadedAsset with operation ID and asset details.
        """
        ext = os.path.splitext(file_path)[1].lower()
        mime = _MIME_MAP.get(ext, "image/png")
        return self._upload(file_path, name, description, "Image", mime)

    def upload_audio(self, file_path: str, name: str,
                     description: str = "") -> UploadedAsset:
        """
        Upload an audio asset (OGG, MP3).

        Args:
            file_path: Path to the audio file.
            name: Display name for the asset.
        """
        ext = os.path.splitext(file_path)[1].lower()
        mime = _MIME_MAP.get(ext, "audio/ogg")
        return self._upload(file_path, name, description, "Audio", mime)

    def upload_model(self, file_path: str, name: str,
                     description: str = "") -> UploadedAsset:
        """
        Upload a 3D model asset (FBX).

        Args:
            file_path: Path to the .fbx file.
            name: Display name for the asset.
        """
        return self._upload(file_path, name, description, "Model", "model/fbx")

    def upload_auto(self, file_path: str, name: str,
                    description: str = "") -> UploadedAsset:
        """
        Automatically detect asset type from file extension and upload.

        Supports: .png, .jpg, .jpeg, .bmp, .tga, .ogg, .mp3, .fbx
        """
        ext = os.path.splitext(file_path)[1].lower()
        asset_type = _TYPE_MAP.get(ext)
        if not asset_type:
            raise ValueError(f"Unsupported file type: {ext}")
        mime = _MIME_MAP[ext]
        return self._upload(file_path, name, description, asset_type, mime)

    def get_operation_status(self, operation_id: str) -> dict:
        """
        Check the status of an upload operation.
        Upload processing can take a few seconds after the initial request.

        Args:
            operation_id: The operation ID from an UploadedAsset.

        Returns:
            dict with done (bool) and asset details when complete.
        """
        r = requests.get(
            f"https://apis.roblox.com/assets/v1/{operation_id}",
            headers={"x-api-key": self._key},
            timeout=self._timeout,
        )
        r.raise_for_status()
        return r.json()

    def wait_for_asset(self, operation_id: str,
                       max_wait: int = 30,
                       poll_interval: float = 2.0) -> Optional[UploadedAsset]:
        """
        Poll until an upload operation completes.

        Args:
            operation_id: Operation ID from upload.
            max_wait: Maximum seconds to wait.
            poll_interval: Seconds between polls.

        Returns:
            UploadedAsset when done, None on timeout.
        """
        import time
        deadline = time.time() + max_wait
        while time.time() < deadline:
            data = self.get_operation_status(operation_id)
            if data.get("done"):
                return UploadedAsset.from_dict(data)
            time.sleep(poll_interval)
        return None
