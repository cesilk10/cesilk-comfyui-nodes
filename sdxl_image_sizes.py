class SdxlImageSizes:
    SDXL_SIZES = {
        "1024x1024 (1:1)": (1024, 1024),
        "576x1728 (1:3)": (576, 1728),
        "1728x576 (3:1)": (1728, 576),
        "832x1216 (2:3)": (832, 1216),
        "1216x832 (3:2)": (1216, 832),
        "896x1152 (3:4)": (896, 1152),
        "1152x896 (4:3)": (1152, 896),
        "1152x1536 (3:4)": (1152, 1536),
        "640x896 (5:7)": (640, 896),
        "896x640 (7:5)": (896, 640),
        "640x1536 (5:12)": (640, 1536),
        "1536x640 (12:5)": (1536, 640), 
        "768x1344 (9:16)": (768, 1344),
        "1344x768 (16:9)": (1344, 768),
        "672x1568 (9:21)": (672, 1568),
        "1568x672 (21:9)": (1568, 672),
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
    CATEGORY = "🐅cesilk_nodes"

    def get_dimensions(self, size):
        w_str, h_str = size.split(" ")[0].split("x")
        return int(w_str), int(h_str)