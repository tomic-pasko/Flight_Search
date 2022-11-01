from app import app
from app import db
from models import Flight, Location, FlightForm
from services import FlightSearch
from flask import render_template, request, jsonify
import psycopg2
import psycopg2.extras
from iata_scrape import scrape_wiki

# Line below only required once, when creating db
# with app.app_context():
#     db.create_all()


# all routes below
@app.route("/", methods=['GET', 'POST'])
def home():
    form = FlightForm()

    if form.validate_on_submit():

        origin_location_code = form.originLocationCode.data.upper()
        dest_location_code = form.destLocationCode.data.upper()
        departure_date = form.departureDate.data
        return_date = form.returnDate.data
        num_adults = form.adults.data
        currency_code = form.currencyCode.data
        max_flights_returned = form.max.data

        fs = FlightSearch()

        # get Token in order to make API call
        token = fs.get_token()
        print(token)

        # API call
        flightInfo = fs.get_flight_offers(token=token, originLocationCode=origin_location_code,
                                          destLocationCode=dest_location_code, departureDate=departure_date,
                                          returnDate=return_date, adults=num_adults, currencyCode=currency_code,
                                          max_flights=max_flights_returned)

        # check if response contains error
        if type(flightInfo) is dict and 'errors' in flightInfo.keys():
            return render_template('error.html', flights=flightInfo)

        # check if there are returned flights
        elif type(flightInfo) is dict and flightInfo['meta']['count'] == 0:
            return render_template('error.html', flights=flightInfo)

        else:
            # get coordinates of stops of all flights in departure way
            coordinates = fs.get_stops_coordinates(flightInfo)
            print(coordinates)

            # get great circle distances between stops of all flights in departure way
            distances = fs.get_great_circle_distances(coordinates)

            # check if there is a record in db
            searchLink = flightInfo[0]['searchLink']
            already_searched_flights = Flight.query.filter_by(searchLink=searchLink).all()

            if already_searched_flights:
                # render flights from local db
                return render_template('flight.html', flights=already_searched_flights, distances=distances)
            else:
                # add new flights to database and render them
                db.session.execute(Flight.__table__.insert(), flightInfo)
                db.session.commit()
                # render flight.html with info about low-cost flights
                return render_template('flight.html', flights=flightInfo, distances=distances)

    return render_template('index.html', form=form)


# hidden route
@app.route("/iatascrape", methods=['GET', 'POST'])
def iata_scrape():

    iata_data = scrape_wiki()

    db.session.execute(Location.__table__.insert(), iata_data)
    db.session.commit()

    return render_template('iatascrape.html')

# search for Airport IATA code from db table Location
# search all rows that match user input (city name)
@app.route("/ajaxlivesearch", methods=["POST", "GET"])
def ajaxlivesearch():
    if request.method == 'POST':
        search_word = request.form['query'].lower().capitalize()
        print(search_word)
        if search_word == '':
            airports = None
            numrows = 0
        else:
            airports = Location.query.filter_by(location_served_city=search_word)
            numrows = int(airports.count())
            print(numrows)
        return jsonify({'htmlresponse': render_template('response.html', airports=airports, numrows=numrows)})


if __name__ == '__main__':
    app.run()


