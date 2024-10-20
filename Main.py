from flask import Flask, render_template, request
import requests
import keys

app = Flask(__name__)


#creating dictionaries for information
country_info = {
    "name": "",
    "capital": "",
    "population": "",
    "languages": ""
}

weather_info = {
    "temperature": "",
    "feels_like": "",
    "humidity": "",
}

time_info = {
    "time": ""
}





#getting country information from RESTcountries
def get_all_countries():
    url = "https://restcountries.com/v3.1/all?fields=name,capital,population,languages"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        country_names = sorted([country["name"]["common"] for country in data])
        return country_names
    return []

#assigning values to dictionary
def get_country_info(selected_country):
    url = "https://restcountries.com/v3.1/all?fields=name,capital,population,languages"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        #looping through all values in the data to check if country matches the user input
        for country in data:
            if country["name"]["common"].lower() == selected_country.lower():
                country_info["name"] = country["name"]['common']
                country_info["capital"] = country["capital"][0]
                country_info["population"] = format(country["population"], ",")
                country_info["languages"] = ",".join(country.get("languages", {}).values())

                return country_info
        else:
            return []

#convert location to lat and lon
def convert_name(city_name):
    url = (f"https://api.openweathermap.org/geo/1.0/direct?q={city_name},&appid="
           f"{keys.open_weather_api_key}")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        city_lat = data[0]["lat"]
        city_lon = data[0]["lon"]
        return city_lat, city_lon

#get weather function from openweather
def get_weather_info(city_coords):

    url = (f"https://api.openweathermap.org/data/2.5/forecast?lat={city_coords[0]}&lon="
           f"{city_coords[1]}&appid={keys.open_weather_api_key}&units=metric")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for temp in data["list"]:
            weather_info["temperature"] = round(temp["main"]["temp"])
            weather_info["feels_like"] = round(temp["main"]["feels_like"])
            weather_info["humidity"] = round(temp["main"]["humidity"])
            return weather_info
    else:
        return []

#get time information from coordinates of capital
def get_time_info(city_coords):
    url = (f"https://api.timezonedb.com/v2.1/get-time-zone?key="
           f"{keys.time_db_api_key}&by=position&lat"
           f"={city_coords[0]}&lng={city_coords[1]}&format=json&fields=formatted")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        time_info["time"] = data["formatted"]
        return time_info["time"]


@app.route('/', methods=['GET', 'POST'])
def index():
    #declaring empty variables
    country_data = None
    weather = None
    time = None

    country_names = get_all_countries()
    if request.method == 'POST':
        #get selected country from user
        selected_country = request.form.get('country')

        #get info about selected country
        country_data = get_country_info(selected_country)

        #convert capital of selected country to latitude and longitude
        capital_coords = convert_name(country_data["capital"])

        #get weather of capital from lat and lon
        weather= get_weather_info(capital_coords)

        #get time from lat and lon
        time = time_info = get_time_info(capital_coords)



    return render_template('index.html', country_data=country_data, country_names =
    country_names, weather=weather, time=time)


if __name__ == '__main__':
    app.run()