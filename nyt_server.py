from bottle import route, run, get, static_file
from pdf2image import convert_from_bytes
import requests
from datetime import date
import datetime
import time


@route('/image/<filename>')
def server_static(filename):
    return static_file("nyt_fp.png", root='./')

@get('/')
def main():
    today = date.today()

    i = 0
    while i < 3:
        try:
            pdf = requests.get("https://static01.nyt.com/images/%s/%s/%s/nytfrontpage/scan.pdf" % (today.strftime("%Y"), today.strftime("%m"), today.strftime("%d")), stream=True)
            images = convert_from_bytes(pdf.content, dpi=600, fmt="png", grayscale=True, size=(1480, None), use_cropbox=True, hide_annotations=True)
            image = images[0]
            image.save('nyt_fp.png', 'png')

            return '<body style="margin-left: -23px; margin-top: -35px;">' + \
            '<img src="image/nyt_fp.png?' + str(time.time()) + '" />' + \
            '</body>'
        except:
            return '<body>Error</body>'
        i += 1
        if pdf.status_code == 404:
            today = today - datetime.timedelta(i)
        else:
            break


run(host='0.0.0.0', port=8001)

