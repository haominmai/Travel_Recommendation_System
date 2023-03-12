from flask import Flask, render_template, request
import pandas as pd
import warnings
warnings.simplefilter(action = 'ignore', category = FutureWarning)
import googlemaps
import sqlite3
import json 
import calendar
import datetime


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['POST'])
def search():
    city = request.form['city']
    interest = request.form['interest']
    places = search_place(city, interest)
    df = info(places)
    #save_to_database(df)
    return render_template('results.html', city = city, interest = interest, table = df)

# APP FUNCTIONS

# Johnny's - AIzaSyCpcurR1TxU1Cgp_5Hv6PeUZ_p-qc-WD1M

api_key = 'AIzaSyCpcurR1TxU1Cgp_5Hv6PeUZ_p-qc-WD1M'

def search_place(city, interest):
    '''
    Input:
        city name, and interest (bar, amusement park, food, etc.)
    Output:
        An array of all places which are arrays of objects including
        their name, address, rating, etc.
    '''
    gmaps = googlemaps.Client(key = api_key)
    places_result = gmaps.places(location = city, query = interest)
    places_list = places_result['results']
    return(places_list) 

    
def info(places):
    """
    Extract useful information from the 
    list of places and return a dataframe
    
    city: the name of the city 
    interest: the type of interests like restaurant, museums
    
    """
    columns = ['result','name', 'address', 'latitude', 'longitude', 'rating', 'rating_numbers', 'open_hour']
    df = pd.DataFrame(columns = columns)
    
    for place in places:
        name = place['name']
        address = place['formatted_address']
        latitude = place['geometry']['location']['lat']
        longitude = place['geometry']['location']['lng']
        rating = place.get('rating', 0) # Use 0 as default rating if not found
        rating_numbers = place.get('user_ratings_total', 0) # Use 0 as default rating count if not found
        open_hour = reorganize_opening_hours(place['place_id'])

        df = pd.concat([df, pd.DataFrame({
            'result': len(df) + 1,
            'name': [name],
            'address': [address],
            'latitude': [latitude],
            'longitude': [longitude],
            'rating': [rating],
            'rating_numbers': [rating_numbers],
            'open_hour': [open_hour]
        })])

    
    df.reset_index(drop = True, inplace = True)
    
    
    return df


gmaps = googlemaps.Client(key=api_key)

def get_place_details(place_id):
    
    # call place API with the given place id
    place_details = gmaps.place(place_id=place_id, fields=['opening_hours'])
    
    # check if the 'opening_hours' field is present in the response
    if 'opening_hours' in place_details['result']:
        opening_hours = place_details['result']['opening_hours']
        return opening_hours
    else:
        return None


def reorganize_opening_hours(place_id):
    
    opening_hours = get_place_details(place_id)
    
    # check if the 'opening_hours' field is present in the response
    if opening_hours:
        opening_hours = json.dumps(opening_hours)
        opening_hours_dict = json.loads(opening_hours)
        
        # initialize the opening hours dictionary with default values
        periods = opening_hours_dict['periods']
        formatted_periods = []
        
        # loop through each period in the periods list
        for period in periods:
            
            # check if the 'open' field is present in the current period
            if 'open' in period:
                # get the start and end times for the period
                start_time = period['open']['time']
                formatted_start_time = start_time[:2] + ':' + start_time[2:]
                
                # get the day of the week for the period and update the opening hours dictionary
                day_number = period['open']['day']
                day_name = (datetime.datetime(2023, 3, 13) + datetime.timedelta(days=day_number - 1)).strftime('%A')
                
                # check if the 'close' field is present in the current period
                if 'close' in period:
                    end_time = period['close']['time']
                    formatted_end_time = end_time[:2] + ':' + end_time[2:]
                    formatted_periods.append(f"{day_name}: {formatted_start_time} - {formatted_end_time}")
                else:
                    formatted_periods.append(f"{day_name}: {formatted_start_time} - Unknown closing time")
            
        return(formatted_periods) # print("\n".join(formatted_periods))
        
    else:
        return ('No opening hours found.')

        
def save_to_database(df):
    # Connect to the database
    conn = sqlite3.connect('places.db')
    cur = conn.cursor()

    # Drop the places table if it already exists
    cur.execute("DROP TABLE IF EXISTS places")

    # Create a new places table
    cur.execute("CREATE TABLE places (name TEXT, address TEXT, latitude REAL, longitude REAL, rating INTEGER, rating_numbers INTEGER, types TEXT)")

    # Insert the data into the places table
    for row in df.itertuples(index = False):

        cur.execute("INSERT INTO places VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (str(row.name), str(row.address), float(row.latitude), float(row.longitude), float(row.rating), float(row.num_reviews), str(row.types)))
        
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)

    

    
    
    
