from flask import Flask, render_template, request, url_for
import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
import googlemaps
import sqlite3
import json
import calendar
import datetime
import plotly.express as px
import plotly
import plotly.io as pio
import plotly.graph_objs as go
pio.renderers.default='iframe'

# Johnny's API key- AIzaSyCpcurR1TxU1Cgp_5Hv6PeUZ_p-qc-WD1M
api_key = 'AIzaSyCpcurR1TxU1Cgp_5Hv6PeUZ_p-qc-WD1M'
# Johnny's mapbox token - pk.eyJ1Ijoiam9obm55Y2hpbmc4MTgiLCJhIjoiY2xmbHZxdGgwMDE4OTN2cHB5c3poeHRvOSJ9.3Sz5VR_4T9azkwqrmTk1uA
token = 'pk.eyJ1Ijoiam9obm55Y2hpbmc4MTgiLCJhIjoiY2xmbHZxdGgwMDE4OTN2cHB5c3poeHRvOSJ9.3Sz5VR_4T9azkwqrmTk1uA'
gmaps = googlemaps.Client(key=api_key)

app = Flask(__name__)


from test_csv import get_random_rec
@app.route('/')
def home():
    cur_index = int(request.args.get('cur_index', '0'))
    recommend, cur_index = get_random_rec(cur_index)
    return render_template('home.html', recommend=recommend, cur_index=cur_index)



@app.route('/search', methods=['POST'])
def search():
    current_plan = []
    city = request.form['city']
    interest = request.form['interest']
    places, lat, lng, names = search_place(city, interest)
    fig = create_figure(lat = lat, lng = lng, names=names)
    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    df = info(places)
    save_to_database(df)
    return render_template('results.html', city=city, interest=interest, table=df, current_plan=current_plan,fig_json=fig_json)


# APP FUNCTIONS

def search_place(city, interest):
    '''
    Input:
        city name, and interest (bar, amusement park, food, etc.)
    Output:
        An array of all places which are arrays of objects including
        their name, address, rating, etc.
    '''
    gmaps = googlemaps.Client(key=api_key)
    city_gmap = gmaps.places(query=city)
    city_location = city_gmap['results'][0]['geometry']['location']
    places_result = gmaps.places(location=city_location, query=interest)
    places_list = places_result['results']
    lat = []
    lng = []
    names = []
    for i in places_list:
        lat.append(i['geometry']['location']['lat'])
        lng.append(i['geometry']['location']['lng'])
        names.append(i['name'])
    return (places_list, lat, lng, names)


def info(places):
    """
    Extract useful information from the
    list of places and return a dataframe

    city: the name of the city
    interest: the type of interests like restaurant, museums

    """
    columns = ['result', 'name', 'address', 'rating', 'rating_numbers', 'open_hour']

    df = pd.DataFrame(columns=columns)

    for place in places:
        name = place['name']
        address = place['formatted_address']
        rating = place.get('rating', 0)  # Use 0 as default rating if not found
        rating_numbers = place.get('user_ratings_total', 0)  # Use 0 as default rating count if not found
        open_hour = reorganize_opening_hours(place['place_id'])

        df = pd.concat([df, pd.DataFrame({
            'result': len(df) + 1,
            'name': [name],
            'address': [address],
            'rating': [rating],
            'rating_numbers': [rating_numbers],
            'open_hour': [open_hour]
        })])

    df.reset_index(drop=True, inplace=True)
    return df


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
    if opening_hours and 'periods' in opening_hours:
        periods = opening_hours['periods']
        
        # initialize the opening hours dictionary with default values
        opening_hours_dict = {}
        
        # loop through each period in the periods list
        for period in periods:
            
            # check if the 'open' field is present in the current period
            if 'open' in period:
                # get the start and end times for the period
                start_time = period['open']['time']
                formatted_start_time = start_time[:2] + ':' + start_time[2:]
                
                # get the day of the week for the period and update the opening hours dictionary
                day_number = period['open']['day']
                day_name = ((datetime.datetime(2023, 3, 13) + datetime.timedelta(days=day_number - 1)).strftime('%A') + ":").ljust(10," ")
                
                # check if the 'close' field is present in the current period
                if 'close' in period:
                    end_time = period['close']['time']
                    formatted_end_time = end_time[:2] + ':' + end_time[2:]
                    
                    # check if the day name already exists in the dictionary
                    if day_name in opening_hours_dict:

                        opening_hours_dict[day_name].append(f"{' ' * len(day_name)}  {formatted_start_time} - {formatted_end_time}")
                    else:
                        opening_hours_dict[day_name] = [f"{day_name}  {formatted_start_time} - {formatted_end_time}"]
                else:
                    # check if the day name already exists in the dictionary
                    if day_name in opening_hours_dict:
                        opening_hours_dict[day_name].append(f"{' ' * len(day_name)}  {formatted_start_time} - Unknown closing time")
                    else:
                        opening_hours_dict[day_name] = [f"{day_name}  {formatted_start_time} - Unknown closing time"]
        
        # convert the dictionary values into a list of formatted strings
        formatted_periods = []
        for day, hours in opening_hours_dict.items():
            formatted_periods.extend(hours)
            
        return formatted_periods
    
    else:
        return ['No opening hours found.']


def create_figure(lat,lng,names):
    fig = go.Figure(data=go.Scattermapbox(
        lat=lat, lon=lng, mode='markers+text', 
        text=names, hovertext=names, hovertemplate='<b>%{text}</b><extra></extra>'
        ))
    fig.update_layout(
        mapbox={
            'accesstoken': token,
            'center': {'lat': lat[0], 'lon': lng[0]},
            'zoom': 12
        },
        margin=dict(l=0, r=0, t=0, b=0) # remove margins
    )
    fig.update_traces(
        marker_size=10,
        textposition='top center',
        hoverlabel_namelength=-1,
    )
    return fig



def save_to_database(df):
    # Connect to the database
    conn = sqlite3.connect('places.db')
    cur = conn.cursor()

    # Drop the places table if it already exists
    cur.execute("DROP TABLE IF EXISTS places")

    # Create a new places table
    cur.execute(
        "CREATE TABLE places (name TEXT, address TEXT, rating INTEGER, rating_numbers INTEGER, open_hour TEXT)")

    # Insert the data into the places table
    for row in df.itertuples(index=False):
        cur.execute("INSERT INTO places VALUES (?, ?, ?, ?, ?)",
                    (str(row.name), str(row.address), float(row.rating), float(row.rating_numbers), str(row.open_hour)))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


if __name__ == '__main__':
    app.run(debug=True)













    
    
    
