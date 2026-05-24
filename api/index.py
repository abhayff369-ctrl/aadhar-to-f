from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
import ssl
from requests.adapters import HTTPAdapter
from urllib.parse import urljoin

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

            base = "https://epos.bihar.gov.in"

            session = requests.Session()

            session.mount("https://", TLSAdapter())

            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            response = session.get(
                base,
                headers=headers,
                timeout=30
            )

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            links = []

            for tag in soup.find_all("a"):

                href = tag.get("href")

                if href:

                    full_url = urljoin(base, href)

                    links.append({
                        "text": tag.get_text(strip=True),
                        "url": full_url
                    })

            jsps = []

            for link in links:

                if ".jsp" in link["url"]:

                    try:

                        r = session.get(
                            link["url"],
                            headers=headers,
                            timeout=20
                        )

                        s = BeautifulSoup(
                            r.text,
                            "html.parser"
                        )

                        forms = []

                        for form in s.find_all("form"):

                            inputs = []

                            for inp in form.find_all("input"):

                                inputs.append({
                                    "name": inp.get("name"),
                                    "type": inp.get("type")
                                })

                            forms.append({
                                "action": form.get("action"),
                                "method": form.get("method"),
                                "inputs": inputs
                            })

                        jsps.append({

                            "page": link["url"],

                            "title":
                            s.title.text
                            if s.title else "",

                            "forms_found":
                            len(forms),

                            "forms":
                            forms

                        })

                    except Exception as e:

                        jsps.append({
                            "page": link["url"],
                            "error": str(e)
                        })

            output = {

                "success": True,

                "total_links": len(links),

                "jsp_pages": jsps

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
