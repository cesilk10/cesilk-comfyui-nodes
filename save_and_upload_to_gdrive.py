import json
import os
import re
from datetime import datetime, timedelta, timezone

import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo

import folder_paths
try:
    from comfy.cli_args import args
except Exception:
    class _A: disable_metadata = False
    args = _A()

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


NODE_CATEGORY = "🐅cesilk_nodes"

SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.file"
]


def current_jst_date() -> str:
    # 例: "2025-08-13"
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst).strftime("%Y-%m-%d")


def replace_datetime_placeholders(text: str) -> str:
    """
    @@...@@ で囲まれた部分を datetime.strftime の書式として解釈し、
    現在の日本時間で置換する。
    """
    jst = timezone(timedelta(hours=9))  # UTC+9
    now = datetime.now(jst)

    def repl(match):
        fmt = match.group(1)
        return now.strftime(fmt)

    return re.sub(r"@@(.*?)@@", repl, text)


def _ensure_auth(node_dir):
    creds = None
    token_path = os.path.join(node_dir, "token.json")
    credentials_path = os.path.join(node_dir, "credentials.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    service = build("drive", "v3", credentials=creds)
    return service


def _upload_file(service, root_id, sub_id, filename):
    try:
        # search folder
        files = []
        page_token = None
        while True:
            q = (
                f"'{root_id}' in parents and "
                f"mimeType = 'application/vnd.google-apps.folder' and "
                f"name = '{sub_id}' and trashed = false"
            )
            response = (
                service.files()
                .list(
                    q=q,
                    spaces="drive",
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token,
                )
                .execute()
            )
            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

        if files:
            target_folder_id = files[0].get("id", "")
            print(f'Found file: {sub_id}, {target_folder_id}')
        else:

            # create folder
            folder_metadata = {
                "name": sub_id,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [root_id],
            }
            folder = service.files().create(body=folder_metadata, fields="id").execute()
            target_folder_id = folder.get("id")
            print(f'target_folder_id: "{target_folder_id}".')

        # file upload
        file_metadata = {"name": os.path.basename(filename), "parents": [target_folder_id]}
        media = MediaFileUpload(filename, mimetype="image/png", resumable=True)
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        print(f'File ID: {file.get("id")}')

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file.get("id")


class SaveAndUploadToGoogleDrive:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.compress_level = 4  # PNG 圧縮

        # 認証ファイル検索用にこの .py の場所を覚えておく
        self._node_dir = os.path.dirname(os.path.abspath(__file__))
        self.root_id = os.getenv("GDRIVE_ROOT_ID")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to save."}),
                "gdrive_upload": ("BOOLEAN", {"default": False}),
                "directory": ("STRING", {"default": "@@%Y-%m-%d@@"}),
                "filename_prefix": ("STRING", {"default": "@@%H%M%S@@"}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_image_to_gdrive"
    CATEGORY = NODE_CATEGORY
    OUTPUT_NODE = True

    def save_image_to_gdrive(self, images, gdrive_upload, directory, filename_prefix,
                             prompt=None, extra_pnginfo=None):
        if images is None or len(images) == 0:
            return {"ui": {"images": []}}

        directory = replace_datetime_placeholders(directory)
        filename_prefix = os.path.join(directory, filename_prefix)
        filename_prefix = replace_datetime_placeholders(filename_prefix)

        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0]
        )

        results = []

        for batch_number, image in enumerate(images):
            # tensor -> uint8 HWC
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            # PNG メタデータ
            metadata = None
            if not getattr(args, "disable_metadata", False):
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            # ローカル保存
            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}.png"
            local_path = os.path.join(full_output_folder, file)
            img.save(local_path, pnginfo=metadata, compress_level=self.compress_level)

            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1

            # Drive アップロード
            if gdrive_upload:
                service = _ensure_auth(self._node_dir)
                _upload_file(service, self.root_id, directory, local_path)

        return {"ui": {"images": results}}
