from flask import Flask, render_template, request
import pandas as pd
import warnings
warnings.simplefilter(action = 'ignore', category = FutureWarning)

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



import googlemaps

api_key = 'YOUR_API_KEY'

def search_place(city, interest):
    gmaps = googlemaps.Client(key = api_key)
    places_result = gmaps.places(query = city, type = interest)
    places_list = places_result['results']
    return(places_list) 

#places = search_place(city,interest)
    
import pandas as pd
def info(places):
    columns = ['name', 'address', 'latitude', 'longitude', 'rating', 'rating_numbers', 'open_now', 'types']
    df = pd.DataFrame(columns = columns)
    
    for place in places:
        name = place['name']
        address = place['formatted_address']
        latitude = place['geometry']['location']['lat']
        longitude = place['geometry']['location']['lng']
        rating = place.get('rating', 0) # Use 0 as default rating if not found
        rating_numbers = place.get('user_ratings_total', 0) # Use 0 as default rating count if not found
        open_now = place.get('opening_hours').get('open_now')
        types = place.get('types')

        df = pd.concat([df, pd.DataFrame({
            'name': [name],
            'address': [address],
            'latitude': [latitude],
            'longitude': [longitude],
            'rating': [rating],
            'rating_numbers': [rating_numbers],
            'open_now': [open_now],
            'types': [types],
        })])

    
    df.reset_index(drop = True, inplace = True)
    
    
    return df


import warnings
warnings.simplefilter(action = 'ignore', category = FutureWarning)

#df = info(places)

import sqlite3

def save_to_database(df):
    # Connect to the database
    conn = sqlite3.connect('places.db')
    cur = conn.cursor()

    # Drop the places table if it already exists
    cur.execute("DROP TABLE IF EXISTS places")

    # Create a new places table
    cur.execute("CREATE TABLE places (name TEXT, address TEXT, latitude REAL, longitude REAL, rating INTEGER, rating_numbers INTEGER, open_now TEXT, types TEXT)")

    # Insert the data into the places table
    for row in df.itertuples(index = False):

        cur.execute("INSERT INTO places VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (str(row.name), str(row.address), float(row.latitude), float(row.longitude), float(row.rating), int(row.rating_numbers), str(row.open_now), str(row.types)))
        
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
#save_to_database(df)




if __name__ == '__main__':
    app.run(debug=True)

    

    
    
    
