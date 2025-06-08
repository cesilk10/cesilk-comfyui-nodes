class SdxlImageSizes:
    SDXL_SIZES = {
        "1024x1024 (1:1)": (1024, 1024),
        "1152x896 (4:3)": (1152, 896),
        "896x1152 (3:4)": (896, 1152),
        "1152x1536 (3:4)": (1152, 1536),
        "1216x832 (3:2)": (1216, 832),
        "832x1216 (2:3)": (832, 1216),
        "1344x768 (16:9)": (1344, 768),
        "768x1344 (9:16)": (768, 1344)
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "size": (list(cls.SDXL_SIZES.keys()), {})
            }
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "get_dimensions"
    CATEGORY = "cesilk_nodes"

    def get_dimensions(self, size):
        w_str, h_str = size.split(" ")[0].split("x")
        return int(w_str), int(h_str)