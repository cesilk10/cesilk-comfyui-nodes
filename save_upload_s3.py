import os
import json
from datetime import datetime, timedelta

import boto3
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from comfy.cli_args import args
import folder_paths

# AWS Settings
session = boto3.Session(profile_name="default")
s3 = session.client("s3", region_name="ap-northeast-1")


def current_jst_date() -> str:
    return (datetime.utcnow() + timedelta(hours=9)).strftime("%Y-%m-%d")


class SaveAndUploadToS3:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to save."}),
                "filename_prefix": ("STRING", {"default": "%year%-%month%-%day%/%hour%%minute%%second%", "tooltip": "The prefix for the file to save. This may include formatting information such as %date:yyyy-MM-dd% or %Empty Latent Image.width% to include values from nodes."}),
                "s3_upload": ("BOOLEAN", {"default": False}),
                "s3_bucket": ("STRING", {"default": "sd-image-88"}),
                "s3_path": ("STRING", {"default": ""}),
            },
            "hidden": {
                "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_image_to_s3"
    CATEGORY = "cesilk_nodes"
    OUTPUT_NODE = True

    def save_image_to_s3(self, images, filename_prefix, s3_upload, s3_bucket, s3_path, prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        results = list()
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1

            if s3_upload:
                if not s3_path:
                    s3_path = f"outputs/{current_jst_date()}/"
                key = os.path.join(s3_path, file)
                s3.upload_file(os.path.join(full_output_folder, file), s3_bucket, key)
                print(f"upload image success. S3 Key: {key}")

        return { "ui": { "images": results } }
