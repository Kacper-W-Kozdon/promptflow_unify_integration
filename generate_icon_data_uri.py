from PIL import Image
import base64

def image_to_data_uri(image_path):
    """Converts an image file to a data URI."""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded_string}"

# Specify the path to your icon file
icon_path = "unify_icon.png"  # Since it's in the root folder
data_uri = image_to_data_uri(icon_path)

# Print the data URI 
print(data_uri)