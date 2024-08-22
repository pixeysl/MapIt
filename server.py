from flask import Flask, render_template, request
from tabelog import parse
from waitress import serve

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/tabelog')
def get_info():
    url = request.args.get('url')

    # Check for empty strings or string with only spaces
    if not bool(url.strip()):
        # You could render "City Not Found" instead like we do below
        url = "not found"

    weather_data = parse(url)

    # City is not found by API
    if not weather_data['cod'] == 200:
        return render_template('city-not-found.html')

    return render_template(
        "weather.html",
        title=weather_data["name"],
        status=weather_data["weather"][0]["description"].capitalize(),
        temp=f"{weather_data['main']['temp']:.1f}",
        feels_like=f"{weather_data['main']['feels_like']:.1f}"
    )


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
