from flask import Flask, request, render_template
import mbta_helper

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        place_name = request.form.get('placeName', '')
        station_name, wheelchair_accessible, arrivals, latitude, longitude = mbta_helper.find_stop_near(place_name)
        
        if station_name:  
            weather_info = mbta_helper.get_weather(latitude, longitude) if latitude and longitude else None
            return render_template('result.html', station_name=station_name, wheelchair_accessible=wheelchair_accessible, arrivals=arrivals, weather_info=weather_info)
        else:
            error_message = "No MBTA station found near this location."
            return render_template('index.html', error_message=error_message)
    return render_template('index.html', error_message=None)



if __name__ == '__main__':
    app.run(debug=True)
