from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskapp.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UploadForm(FlaskForm):
    company_name = StringField('Company Name',
                           validators=[DataRequired()])
    report_img_file = FileField('Upload Report Image', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png'])])
    comment = StringField('Comments(Optional)')
    upload = SubmitField('Upload')

class SearchForm(FlaskForm):
    search_box = StringField('Search Box',
                           validators=[DataRequired()])

    search = SubmitField('Search')

        # 'user_id': 'Mr.Kbul Alam',
        # 'company_name': 'Kashem Steels.Ltd',
        # 'report_text':r'Shoe bed sheet sitting sofa\n ',
        # 'date_posted': 'May 20, 2021',
        # 'report_img' : 'https://picsum.photos/200/200',
        # 'commens' : ''