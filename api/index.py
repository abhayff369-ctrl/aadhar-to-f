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

            month = params.get("month", ["5"])[0]
            year = params.get("year", ["2026"])[0]
            rc = params.get("rc", [""])[0]

            if not rc:

                self.send_response(400)
                self.send_header(
                    "Content-type",
                    "application/json"
                )
                self.end_headers()

                self.wfile.write(json.dumps({
                    "success": False,
                    "message": "rc parameter required"
                }).encode())

                return

            session = requests.Session()

            session.mount(
                "https://",
                TLSAdapter()
            )

            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            url = "https://epos.bihar.gov.in/SRC_Trans_Int.jsp"

            payload = {
                "month": month,
                "year": year,
                "rcno": rc
            }

            response = session.post(
                url,
                data=payload,
                headers=headers,
                timeout=30
            )

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            tables = []

            for table in soup.find_all("table"):

                rows = []

                for tr in table.find_all("tr"):

                    cols = [

                        td.get_text(strip=True)

                        for td in tr.find_all(
                            ["td", "th"]
                        )

                    ]

                    if cols:
                        rows.append(cols)

                if rows:
                    tables.append(rows)

            result = {

                "success": True,

                "month": month,

                "year": year,

                "rc": rc,

                "title":
                soup.title.text
                if soup.title else "",

                "tables_found":
                len(tables),

                "data":
                tables[:5]

            }

            self.send_response(200)

            self.send_header(
                "Content-type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps(
                    result,
                    indent=2
                ).encode()
            )

        except Exception as e:

            self.send_response(500)

            self.send_header(
                "Content-type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(json.dumps({

                "success": False,

                "error": str(e)

            }).encode())
