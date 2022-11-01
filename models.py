from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, IntegerField, validators
from wtforms.validators import InputRequired, Length, ValidationError


class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flightNumber = db.Column(db.String(3))
    originAirport = db.Column(db.String(3))
    destAirport = db.Column(db.String(3))
    departureD = db.Column(db.String(25))
    returnD = db.Column(db.String(25))
    departureSegments = db.Column(db.Integer)
    returnSegments = db.Column(db.Integer)
    num_adults = db.Column(db.Integer)
    currency = db.Column(db.String(3))
    total_price = db.Column(db.Float)
    searchLink = db.Column(db.String(300))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    iata = db.Column(db.String(3))
    airport_name = db.Column(db.String(100))
    location_served = db.Column(db.String(100))
    location_served_city = db.Column(db.String(100))
    lat = db.Column(db.Float)
    long = db.Column(db.Float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# custom functions for validation of form inputs
def no_numbers_allowed(form, field):
    if not field.data.isalpha():
        raise ValidationError('Only alphabet letters allowed (A-Z)')

def num_passengers_check(form, field):
    if field.data < 1:
        raise ValidationError("Number of travellers can't be less then one")



class FlightForm(FlaskForm):
    originLocationCode = StringField(label='From (Airport IATA code)', validators=[InputRequired(), Length(min=3, max=3), no_numbers_allowed])
    destLocationCode = StringField(label='To (Airport IATA code)', validators=[InputRequired(), Length(min=3, max=3), no_numbers_allowed])
    departureDate = DateField(label='Departure Date', format='%Y-%m-%d', validators=[InputRequired()])
    returnDate = DateField(label='Return Date', format='%Y-%m-%d', validators=(validators.Optional(),))
    adults = IntegerField(label='Number of Traveller(s)', validators=[InputRequired(), num_passengers_check])
    currencyCode = SelectField(label='Currency', choices=['USD', 'EUR', 'HRK'])
    max = IntegerField(label='Max number of returned Flights')
    submit = SubmitField('Search Flights')

