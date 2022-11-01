import requests
import os
from models import Location
import greatcircle


###############################################################################
# Site: Amadeus for Developers
# Authorization
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
# Server url
url_amadeus_security = "https://test.api.amadeus.com/v1/security/oauth2/token"

# API - Flight Offers Search
url_flight_offers = "https://test.api.amadeus.com/v2/shopping/flight-offers"

# API - Airport & City Search
url_airport_search = "https://test.api.amadeus.com/v1/reference-data/locations"
################################################################################


class FlightSearch:

    def get_token(self):
        payload = f'client_id={api_key}&client_secret={api_secret}&grant_type=client_credentials'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = requests.request("POST", url=url_amadeus_security, headers=headers, data=payload)
            return response.json()['access_token']
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)



    def get_flight_offers(self, token, originLocationCode, destLocationCode, departureDate, returnDate, adults,
                          currencyCode, max_flights):
        params = {
            'originLocationCode': originLocationCode,
            'destinationLocationCode': destLocationCode,
            'departureDate': departureDate,
            'returnDate': returnDate,
            'adults': adults,
            'currencyCode': currencyCode,
            'max': max_flights
        }
        headers = {
            'Authorization': f'Bearer {token}'
        }
        try:
            response = requests.request('GET', url=url_flight_offers, headers=headers, params=params)

            flights = response.json()


            # check if response contains error
            if 'errors' in flights.keys():
                print('Error')
                return flights

            # check if there are returned flights
            elif flights['meta']['count'] == 0:
                print('No flights')
                return flights

            else:
                # parsing answer from Amadeus
                searchLink = flights['meta']['links']['self']

                flightInfo = []
                stopsD = []
                stopsR = []

                for flight in flights['data']:

                    # stops include origin and final destination
                    stopsD = []
                    stopsR = []

                    # check if it is a two-way flight
                    if len(flight['itineraries']) > 1:
                        returnD = flight['itineraries'][1]['segments'][0]['departure']['at']
                        returnSegments = len(flight['itineraries'][1]['segments'])

                        # check if return flight is flight with stops
                        if len(flight['itineraries'][1]['segments']) > 1:
                            for flight_segment in flight['itineraries'][1]['segments']:
                                stopsR.append(flight_segment['departure']['iataCode'])
                            stopsR.append(destLocationCode)
                        else:
                            stopsR = [destLocationCode, originLocationCode]
                    else:
                        returnD = None
                        returnSegments = None

                    # check if departure flight is flight with stops
                    if len(flight['itineraries'][0]['segments']) > 1:
                        for flight_segment in flight['itineraries'][0]['segments']:
                            stopsD.append(flight_segment['departure']['iataCode'])
                        stopsD.append(destLocationCode)
                    else:
                        stopsD = [originLocationCode, destLocationCode]
                    print(flight['id'])
                    data = {
                        "flightNumber": flight['id'],
                        "originAirport": originLocationCode,
                        "destAirport": destLocationCode,
                        "departureD": flight['itineraries'][0]['segments'][0]['departure']['at'],
                        "returnD": returnD,
                        "departureSegments": len(flight['itineraries'][0]['segments']),
                        "returnSegments": returnSegments,
                        "num_adults": adults,
                        "currency": flight['price']['currency'],
                        "total_price": flight['price']['total'],
                        "searchLink": searchLink,
                        "stopsD": stopsD,
                        "stopsR": stopsR
                    }

                    flightInfo.append(data)

                return flightInfo

        except requests.exceptions.RequestException as e:
            raise SystemExit(e)




    def get_stops_coordinates(self, flightInfo):

        stopsD_coordinates = []
        stopsR_coordinates = []
        # flight counter
        i = 1

        for flight in flightInfo:
            for stop_iata in flight['stopsD']:
                # get lat and long from "Location" table for departure flights
                airport = Location.query.filter_by(iata=stop_iata).first()

                lat = airport.lat
                long = airport.long

                stopsD_coordinates.append({'flight_no': i, 'name': airport.iata, 'latitude1_degrees': lat, 'longitude1_degrees': long})

            for stop_iata in flight['stopsR']:
                # get lat and long from "Location" table for return flights
                airport = Location.query.filter_by(iata=stop_iata).first()
                lat = airport.lat
                long = airport.long

                stopsR_coordinates.append({'flight_no': i, 'name': airport.iata, 'latitude1_degrees': lat, 'longitude1_degrees': long})
            i += 1
        # return list of dict {'flight_no': i, 'airport_iata': airport.iata, 'lat': lat, 'long': long}
        # return all flights, in one way (departure)
        return stopsD_coordinates

    def get_great_circle_distances(self, coordinates):

        starting_cities = []
        destination_cities = []
        distances = []

        # loop through all stops of all returned flights
        for i in range(len(coordinates) - 1):
            # ensure that destination of flights is not appended to starting_cities list
            if coordinates[i]['flight_no'] == coordinates[i + 1]['flight_no']:
                starting_cities.append(coordinates[i])
                destination_cities.append(coordinates[i + 1])

        print(starting_cities)
        print(destination_cities)

        gc = greatcircle.GreatCircle()

        for i in range(0, len(starting_cities)):
            gc.flight_no = starting_cities[i]['flight_no']
            gc.name1 = starting_cities[i]["name"]
            gc.latitude1_degrees = starting_cities[i]["latitude1_degrees"]
            gc.longitude1_degrees = starting_cities[i]["longitude1_degrees"]

            gc.name2 = destination_cities[i]["name"]
            gc.latitude2_degrees = destination_cities[i]["latitude1_degrees"]
            gc.longitude2_degrees = destination_cities[i]["longitude1_degrees"]

            gc.calculate()

            if gc.valid:
                distances.append({'Flight_number': gc.flight_no, 'Start': gc.name1, 'Stop': gc.name2, 'Distance': round(gc.distance_kilometres)})
            else:
                distances.append({'Flight_number': gc.flight_no, 'Start': gc.name1, 'Stop': gc.name2, 'Distance': "No Info"})

        return distances










