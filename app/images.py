import secrets
import os
import io
import base64
from PIL import Image

def save_image(dataURL):
  # retrieve image
  dataURL_cleaned = dataURL.split(',')[1]
  img_data = io.BytesIO(base64.b64decode(dataURL_cleaned))
  img = Image.open(img_data)

  # create secure filepath
  random_hex = secrets.token_hex(8)
  picture_fn = random_hex + '.png'
  app_root_path = os.path.dirname(os.path.abspath(__file__))
  picture_path = os.path.join(app_root_path,'static','drawing_images',picture_fn)

  # save image
  img.save(picture_path)

  return picture_fn