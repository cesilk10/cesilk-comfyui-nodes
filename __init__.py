from .save_upload_s3 import SaveAndUploadToS3
from .save_and_upload_to_gdrive import *
from .sdxl_image_sizes import SdxlImageSizes
from .openai_nodes import *


NODE_CLASS_MAPPINGS = {
    "CESILK_SaveAndUploadToS3": SaveAndUploadToS3,
    "CESILK_SaveAndUploadToGoogleDrive": SaveAndUploadToGoogleDrive,
    "CESILK_SdxlImageSizes": SdxlImageSizes,

    "CESILK_OpenAIImageBatchGenerator": OpenAIImageBatchGenerator,
    "CESILK_OpenAIImageDescriptionToTextfile": OpenAIImageDescriptionToTextfile,
    "CESILK_OpenAIChat": OpenAIChat,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CESILK_SaveAndUploadToS3": "CESILK Save and Upload to S3",
    "CESILK_SaveAndUploadToGoogleDrive": "CESILK Save And Upload To Google Drive",
    "CESILK_SdxlImageSizes": "CESILK SDXL Image Sizes",

    "CESILK_OpenAIImageBatchGenerator": "CESILK OpenAI Image Generator (Batch)",
    "CESILK_OpenAIImageDescriptionToTextfile": "CESILK OpenAI Image Description to Textfile",
    "CESILK_OpenAIChat": "CESILK OpenAI Chat",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
