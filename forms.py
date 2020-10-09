from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, BooleanField, RadioField, SelectField, FileField, PasswordField
from wtforms.validators import InputRequired, Length, Email
from flask_wtf.file import FileField, FileAllowed, FileRequired


class AdminForm(FlaskForm):
    """Form for adding playlists."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class ProductForm(FlaskForm):
    image = FileField('image 1', validators=[FileRequired(), 
    FileAllowed(['jpg','png','jpeg'],'Images only')])
    image1 = FileField('image 2',validators=[ 
    FileAllowed(['jpg','png','jpeg'],'Images only')],)
    image2 = FileField('image 3',validators=[ 
    FileAllowed(['jpg','png','jpeg'],'Images only')],)
    image3 = FileField('image 4',validators=[ 
    FileAllowed(['jpg','png','jpeg'],'Images only')],)
    price = IntegerField('price', validators=[InputRequired()])
    title = StringField('title', validators=[InputRequired(), Length(max=20)])
    description = StringField('description', validators=[InputRequired()])
    category = SelectField('Category', choices=[('bowl','bowl'),('plate','plate'),
    ('box','box'),('miscellaneous','miscellaneous'),('tray','tray'),
    ('sign','sign'),('basket','basket'),
    ('furniture','furniture')])
    available = BooleanField('available')

class PurchaseForm(FlaskForm):
    firstname = StringField('First name', validators=[InputRequired()])
    lastname = StringField('Last name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(),Email(message='Please provide a valid email')])
    message = TextAreaField('Message', validators=[Length(max=200)])
    product_id = StringField('Product Id', validators=[InputRequired()])

class EditForm(FlaskForm):

    changeimage = BooleanField('Change Main Image')
    image = FileField('image 1', validators=[ 
    FileAllowed(['jpg','png','jpeg'],'Images only')], render_kw={'disabled':''} )
    changeimage1 = BooleanField('Change Second Image')
    image1 = FileField('image 2', validators=[ 
    FileAllowed(['jpg','png','jpeg'],'Images only')],render_kw={'disabled':''})
    changeimage2 = BooleanField('Change Third Image')
    image2 = FileField('image 3', validators=[ 
    FileAllowed(['jpg','png','jpeg'],'Images only')],render_kw={'disabled':''})
    changeimage3 = BooleanField('Change Fourth Image')
    image3 = FileField('image 4', validators=[ 
    FileAllowed(['jpg','png','jpeg'],'Images only')],render_kw={'disabled':''})
    price = IntegerField('price', validators=[InputRequired()])
    title = StringField('title', validators=[InputRequired(), Length(max=13)])
    description = StringField('description', validators=[InputRequired()])
    category = SelectField('Category', choices=[('bowl','bowl'),('plate','plate'),
    ('box','box'),('miscellaneous','miscellaneous'),('tray','tray'),
    ('sign','sign'),('basket','basket'),
    ('furniture','furniture')])
    available = BooleanField('available')

class ApiAuth(FlaskForm):

    code = IntegerField('Code', validators=[InputRequired()])