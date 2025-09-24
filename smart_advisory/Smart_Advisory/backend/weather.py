from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib
import requests

API_KEY = "fdf1aeb5f176d7eb550eafe53bb54c8c"  # Your OpenWeatherMap API key

class WeatherHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/weather"):
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            city = query.get("city", [None])[0]
            lang = query.get("lang", ["en"])[0]  # default to English

            if not city:
                self.respond_json({"error": "City is required"}, 400)
                return

            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang={lang}"
                res = requests.get(url)
                data = res.json()

                if data.get("cod") != 200:
                    self.respond_json({"error": f"City not found: {city}"}, 404)
                    return

                weather = {
                    "city": data.get("name", city.title()),
                    "temperature": data["main"]["temp"],
                    "condition": data["weather"][0]["description"].title(),
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"],
                    "rain": data.get("rain", {}).get("1h", 0),
                    "snow": data.get("snow", {}).get("1h", 0)
                }

                self.respond_json(weather)

            except Exception as e:
                self.respond_json({"error": str(e)}, 500)
        else:
            self.send_error(404, "Not Found")

    def respond_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")  # CORS support
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def run():
    server_address = ("", 8000)  # Listening on all interfaces on port 8000
    httpd = HTTPServer(server_address, WeatherHandler)
    print("Server running at http://localhost:8000")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
