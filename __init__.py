from .save_upload_s3 import SaveAndUploadToS3
from .sdxl_image_sizes import SdxlImageSizes


NODE_CLASS_MAPPINGS = {
    "SaveAndUploadToS3": SaveAndUploadToS3,
    "SdxlImageSizes": SdxlImageSizes,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveAndUploadToS3": "Save and Upload to S3",
    "SdxlImageSizes": "SDXL Image Sizes",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
