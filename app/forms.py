from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField,IntegerField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from app.models import User


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

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, firstusername, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.firstusername = firstusername

    def validate_username(self, username):
        if username.data != self.firstusername:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class ArtPieceForm(FlaskForm):
    artname = StringField('Art Name', validators=[DataRequired()])
    arttype = SelectField("Art Type", choices=[('painting', 'Painting'), ('sculptor', 'Sculptor'), ('drawing', 'Drawing')],
                          validators=[DataRequired()])
    size = IntegerField('Size in cm', validators=[DataRequired()])
    weight = IntegerField('Weight in grams', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    dateofcreation = DateField('Date/Year of Creation', validators=[DataRequired()])
    artist = StringField('Artist Name', validators=[DataRequired()])
    artistgender = SelectField('Artist Gender', choices=[('m', 'Male'), ('f', 'Female')],
                               validators=[DataRequired()])
    artistdob = DateField('Artist Date of Birth', validators=[DataRequired()])
    artistdod = DateField('Artist Date of Death')
    coa = BooleanField('Certificate of Authenticity Provided')
    submit = SubmitField('Submit')


class AuctionForm(FlaskForm):
    artname = StringField('Art Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    reserve = IntegerField('Reserve', validators=[DataRequired()])
    consignorname = StringField('Consignor Name', validators=[DataRequired()])
    consignordob = DateField('Consignor Date of Birth', validators=[DataRequired()])
    consignorgender = SelectField('Consignor Gender', choices=[('m', 'Male'), ('f', 'Female')], validators=[DataRequired()])
    submit = SubmitField('Submit')


class TransportForm(FlaskForm):
    artname = StringField('Art Name', validators=[DataRequired()])
    tranportername = StringField('Transporter Name', validators=[DataRequired()])
    transportergender = SelectField('Transporter Gender', choices=[('m', 'Male'), ('f', 'Female')],
                                    validators=[DataRequired()])
    transporterdob = DateField('Transporter Date of Birth', validators=[DataRequired()])
    modeoftransport = SelectField('Mode of Transport', choices=[('land', 'Land'), ('air', 'Air'), ('sea', 'Sea')],
                                  validators=[DataRequired()])
    trackingno = StringField('Delivery Tracking Number', validators=[DataRequired()])
    destination = TextAreaField('Destination', validators=[DataRequired()])
    vehicletemp = IntegerField('Vehicle Temperature (Fahrenheit)')
    deliveryco = StringField('Delivery Company', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SaleForm(FlaskForm):
    artname = StringField('Art Name', validators=[DataRequired()])
    hammerprice = IntegerField('Hammer Price', validators=[DataRequired()])
    buyerspremium = IntegerField('Premium (%)', validators=[DataRequired()])
    saledate = DateField('Sale Date', validators=[DataRequired()])
    auctionhouse = StringField('Auction House', validators=[DataRequired()])
    specialistname = StringField('Specialist Name', validators=[DataRequired()])
    specialistdob = DateField('Specialist Date of Birth', validators=[DataRequired()])
    specialistgender = SelectField('Specialist Gender', choices=[('m', 'Male'), ('f', 'Female')],
                                   validators=[DataRequired()])
    purchasername = StringField('Buyer Name', validators=[DataRequired()])
    purchaserdob = DateField('Buyer Date of Birth', validators=[DataRequired()])
    purchasergender = SelectField('Buyer Gender', choices=[('m', 'Male'), ('f', 'Female')], validators=[DataRequired()])
    submit = SubmitField('Submit')


class DisplayArtForm(FlaskForm):
    artname = StringField('Art Name', validators=[DataRequired()])
    galleryname = StringField('GalleryName', validators=[DataRequired()])
    gallerylocation = StringField('Gallery Location', validators=[DataRequired()])
    galleryowner = StringField('Gallery Owner', validators=[DataRequired()])
    displayroomtemp = IntegerField('Display Room Temperature (Fahrenheit)')
    submit = SubmitField('Submit')


class StoreArtForm(FlaskForm):
    artname = StringField('Art Name', validators=[DataRequired()])
    storagename = StringField('Storage Unit Name', validators=[DataRequired()])
    storagelocation = StringField('Storage Location', validators=[DataRequired()])
    storagetemp = IntegerField('Storage Temperature (Fahrenheit)')
    submit = SubmitField('Submit')


class ActivityForm(FlaskForm):
    activity = SelectField('Activity', choices=[('new', 'New Art'), ('submit', 'Submit Art'),
                                                ('delivery', 'Deliver Art'), ('payment', 'Art Payment'),
                                                ('store', 'Store Art'), ('display', 'Display Art')],
                           validators=[DataRequired()])
    submit = SubmitField('Submit')


class QueryForm(FlaskForm):
    artname = StringField('Art Name', validators=[DataRequired()])
    querytype = SelectField('All previous: ', choices=[('location', 'Location'), ('specialist', 'Specialist'),
                                                       ('hammerprice', 'Hammer Price'), ('auctionhouse', 'AuctionHouse'),
                                                       ('gallery', 'Gallery'), ('buyer', 'Buyer')],
                            validators=[DataRequired()])
    submit = SubmitField('Submit')





