from flask import Flask, render_template, request
import pandas as pd
import warnings
warnings.simplefilter(action = 'ignore', category = FutureWarning)
import googlemaps
import sqlite3

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
    save_to_database(df)
    return render_template('results.html', city = city, interest = interest, table = df.to_html(classes = 'data'))

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

#places = search_place(city,interest)
    
def info(places):
    '''
    Input: 
        places from search_place(city, interest) function.
        Contains an array of all places, which are itself an array of objects 
        which contains all info about each place (name, rating, etc.)
    Output:
        a dataframe which contains all relevant info for each place
    '''
    columns = ['name', 'address', 'latitude', 'longitude', 'rating', 'num_reviews', 'types']
    df = pd.DataFrame(columns = columns)
    
    for place in places:
        name = place['name']
        address = place['formatted_address']
        latitude = place['geometry']['location']['lat']
        longitude = place['geometry']['location']['lng']
        rating = place.get('rating', 0) # Use 0 as default rating if not found
        rating_numbers = place.get('user_ratings_total', 0) # Use 0 as default rating count if not found
        types = place.get('types')

        df = pd.concat([df, pd.DataFrame({
            'name': [name],
            'address': [address],
            'latitude': [latitude],
            'longitude': [longitude],
            'rating': [rating],
            'num_reviews': [rating_numbers],
            'types': [types],
        })], axis = 0)    
    df.reset_index(drop = True, inplace = True)
    return df

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

    

    
    
    
