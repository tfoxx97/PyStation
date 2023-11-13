import os 
import secrets
from PIL import Image
from flask import current_app
from werkzeug.datastructures import FileStorage

def save_picture(form_data: FileStorage):
    '''Save the new post picutre to a given path with unique filename
    
    Parameters: 
    -----------
    form_picture: FileStorage

    Secrets module used to generate random sequence of chars for new filename pre-extension.

    Image is then saved to folder 'static/thumbnails'

    Returns: 
    --------
    picture_fn: str
    '''
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_data.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/thumbnails', picture_fn)

    image = Image.open(form_data)
    image.save(picture_path) 

    return picture_fn