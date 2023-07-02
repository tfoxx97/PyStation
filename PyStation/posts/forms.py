from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    image_optional = FileField('Cover Photo (optional)', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    content = TextAreaField('Content', id="premiumskinsandicons-fluent") #using tinyMCE to add more flavor to textbox
    submit = SubmitField('Post')