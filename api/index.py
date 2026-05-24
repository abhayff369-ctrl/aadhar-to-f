from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
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

            session = requests.Session()

            session.mount("https://", TLSAdapter())

            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            urls = [

                "https://epos.bihar.gov.in",

                "https://epos.bihar.gov.in/SRC_Trans_Int.jsp",

                "https://epos.bihar.gov.in/FPS_Trans_Abstract.jsp",

                "https://epos.bihar.gov.in/AnnavitranTransInt.jsp"

            ]

            final_data = []

            for url in urls:

                try:

                    response = session.get(
                        url,
                        headers=headers,
                        timeout=30
                    )

                    soup = BeautifulSoup(
                        response.text,
                        "html.parser"
                    )

                    forms = []

                    for form in soup.find_all("form"):

                        inputs = []

                        for inp in form.find_all("input"):

                            inputs.append({
                                "name": inp.get("name"),
                                "type": inp.get("type"),
                                "value": inp.get("value")
                            })

                        forms.append({
                            "action": form.get("action"),
                            "method": form.get("method"),
                            "inputs": inputs
                        })

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

                    final_data.append({

                        "url": url,

                        "title":
                        soup.title.text
                        if soup.title else "",

                        "status_code":
                        response.status_code,

                        "forms_found":
                        len(forms),

                        "tables_found":
                        len(tables),

                        "forms":
                        forms[:3],

                        "sample_tables":
                        tables[:1]

                    })

                except Exception as e:

                    final_data.append({

                        "url": url,

                        "error": str(e)

                    })

            output = {

                "success": True,

                "developer": "Abhay Kumar",

                "results": final_data

            }

            self.send_response(200)

            self.send_header(
                "Content-type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps(
                    output,
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
