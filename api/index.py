from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import ssl
from requests.adapters import HTTPAdapter

class TLSAdapter(HTTPAdapter):

    def init_poolmanager(self, *args, **kwargs):

        ctx = ssl.create_default_context()

        ctx.check_hostname = False

        ctx.verify_mode = ssl.CERT_NONE

        ctx.set_ciphers("DEFAULT@SECLEVEL=1")

        kwargs["ssl_context"] = ctx

        return super().init_poolmanager(*args, **kwargs)

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
                    "message": "aadhaar required"
                }).encode())

                return

            session = requests.Session()

            session.mount("https://", TLSAdapter())

            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            url = "https://epos.bihar.gov.in"

            response = session.get(
                url,
                headers=headers,
                timeout=30
            )

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            title = soup.title.text if soup.title else "No Title"

            result = {
                "success": True,
                "aadhaar": aadhaar,
                "title": title,
                "status_code": response.status_code,
                "message": "SSL bypass success"
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            self.wfile.write(
                json.dumps(result).encode()
            )

        except Exception as e:

            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())
