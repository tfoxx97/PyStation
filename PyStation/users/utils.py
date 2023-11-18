import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from PyStation import mail
from PyStation.models import User

def save_picture(form_picture):
    '''Save the profile picutre to a given path with unique filename
    
    Parameters: 
    -----------
    form_picture: FileStorage

    Secrets module used to generate random sequence of chars for new filename pre-extension.

    Image is then resized to fit into tiny circle

    Returns: 
    --------
    picture_fn: str
    '''
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def send_reset_email(user: User):
    ''' Method responsible for sending reset password email. 
    
    Parameters: 
    -----------
    user: User
    
    Method uses Mail object from flask extension to send reset password email to the 
    proper recipient with a given serialized token.
    '''
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                  sender='noreply@shreddit.com', 
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit: {url_for('users.reset_token', token=token, _external=True)} 

If you did not make this request, kindly disregard this email.

Thank you,

-Tyler
'''
    mail.send(msg)