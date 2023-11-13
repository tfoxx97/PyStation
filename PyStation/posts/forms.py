from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed
from flask_ckeditor import CKEditorField

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = CKEditorField('Content', validators=[DataRequired()]) 
    cover_photo = FileField('Cover Photo (optional)', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Post')