from flask import Flask, request, render_template
from prometheus_client import start_http_server, Summary
import requests

app = Flask(__name__)
search_latency = Summary('search_latency_seconds', 'latencyy of /search endpoint in seconds')

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search", methods=["POST"])
@search_latency.time()
def search():
    # Get the search query
    query = request.form["q"]

    # Pass the search query to the Nominatim API to get a location
    location = requests.get(
        "https://nominatim.openstreetmap.org/search",
        {"q": query, "format": "json", "limit": "1"},
    ).json()

    # If a location is found, pass the coordinate to the Time API to get the current time
    if location:
        coordinate = [location[0]["lat"], location[0]["lon"]]

        time = requests.get(
            "https://timeapi.io/api/Time/current/coordinate",
            {"latitude": coordinate[0], "longitude": coordinate[1]},
        )

        return render_template("success.html", location=location[0], time=time.json())

    # If a location is NOT found, return the error page
    else:
        return render_template("fail.html")

# metrics
@app.route('/metrics')
def metrics():
    return generate_latest(search_latency)

if __name__ == "__main__":
    #start prometheus metrics server
    start_http_server(8080)
    app.run(debug=True)
