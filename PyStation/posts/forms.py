from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed
from flask_ckeditor import CKEditorField

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    image_optional = FileField('Cover Photo (optional)', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    content = CKEditorField('Content', validators=[DataRequired()]) 
    submit = SubmitField('Post')