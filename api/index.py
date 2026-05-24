from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):

    def do_GET(self):

        try:

            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)

            aadhaar = params.get("aadhaar", [""])[0]

            if not aadhaar:

                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()

                self.wfile.write(json.dumps({
                    "success": False,
                    "message": "aadhaar parameter required"
                }).encode())

                return

            session = requests.Session()

            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            # Bihar EPDS Website
            url = "https://epos.bihar.gov.in"

            response = session.get(
                url,
                headers=headers,
                timeout=20
            )

            html = response.text

            soup = BeautifulSoup(html, "html.parser")

            title = soup.title.text if soup.title else "No Title"

            # Example scraping output
            data = {
                "success": True,
                "aadhaar": aadhaar,
                "website_title": title,
                "message": "Website connected successfully",
                "ration_card": "XXXXXXXXXX",
                "name": "Demo User",
                "state": "Bihar",
                "status": "Linked"
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps(data).encode())

        except Exception as e:

            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())
