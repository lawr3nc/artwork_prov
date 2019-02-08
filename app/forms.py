from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, DecimalField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class ArtPieceForm(FlaskForm):
    artname = StringField('Art Name', validators=[DataRequired()])
    artist = StringField('Artist Name', validators=[DataRequired()])
    dateofcreation = DateField('Date/Year of Creation', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    size = DecimalField('Size in cm', validators=[DataRequired()])
    weight = DecimalField('Weight in grams', validators=[DataRequired()])
    activity = StringField('Activity', default='New Art')
    submit = SubmitField('Submit')


class AuctionForm(FlaskForm):
    consignorname = StringField('Consignor Name', validators=[DataRequired()])
    consignordob = DateField('Consignor Date of Birth', validators=[DataRequired()])
    consignorgender = SelectField('Consignor Gender', choices=[('m', 'Male'), ('f', 'Female')], validators=[DataRequired()])
    specialistname = StringField('Specialist Name', validators=[DataRequired()])
    actionhouse = StringField('Auction House', validators=[DataRequired()])
    specialistdob = StringField('Specialist Date of Birth', validators=[DataRequired()])
    specialistgender = SelectField('Consignor Gender', choices=[('m', 'Male'), ('f', 'Female')], validators=[DataRequired()])
    activity = StringField('Activity', default='Submit Art')
    submit = SubmitField('Submit')


class TransportForm(FlaskForm):
    tranportername = StringField('Driver Name', validators=[DataRequired()])
    deliveryco = StringField('Delivery Company', validators=[DataRequired()])
    transportergender = SelectField('Transporter Gender', choices=[('m', 'Male'), ('f', 'Female')], validators=[DataRequired()])
    transporterdob = DateField('Driver Date of Birth', validators=[DataRequired()])
    modeoftransport = StringField('Mode of Transport', validators=[DataRequired()])
    trackingno = StringField('Delivery Tracking Number', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    vehicletemp = DecimalField('Vehicle Temperature')
    activity = StringField('Activity', default='Deliver Art')
    submit = SubmitField('Submit')


class PurchaserForm(FlaskForm):
    purchasername = StringField('Buyer Name', validators=[DataRequired()])
    purchaserdob = DateField('Buyer Date of Birth', validators=[DataRequired()])
    purchasergender = SelectField('Purchaser Gender', choices=[('m', 'Male'), ('f', 'Female')], validators=[DataRequired()])
    activity = StringField('Activity', default='Art Payment')
    submit = SubmitField('Submit')


class DisplayArtForm(FlaskForm):
    galleryname = StringField('GalleryName', validators=[DataRequired()])
    gallerylocation = StringField('Gallery Location', validators=[DataRequired])
    galleryowner = StringField('Gallery Owner', validators=[DataRequired()])
    displayroomtemp = DecimalField('Display Room Temperature')
    activity = StringField('Activity', default='Display Art')
    submit = SubmitField('Submit')


class StoreArtForm(FlaskForm):
    storagename = StringField('Storage Unit Name', validators=[DataRequired()])
    storagelocation = StringField('Storage Location', validators=[DataRequired()])
    storagetemp = DecimalField('Storage Temperature', validators=[DataRequired()])
    activity = StringField('Activity', default='Store Art')
    submit = SubmitField('Submit')


class ActivityForm(FlaskForm):
    activity = SelectField('Activity', choices=[('new', 'New Art'), ('submit', 'Submit Art'),
                                                ('delivery', 'Deliver Art'), ('payment', 'Art Payment'),
                                                ('store', 'Store Art'), ('display', 'Display Art')],
                           validators=[DataRequired()])
    submit = SubmitField('Submit')





