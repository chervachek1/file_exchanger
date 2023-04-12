from flask import Flask, render_template, request
import requests
from geopy.distance import geodesic
import socket
from urllib.parse import urlparse
from ip2geotools.databases.noncommercial import DbIpCity

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file_url = request.form['file_url']

        vps1_location = (50.121, 8.4966)  # Frankfurt
        vps2_location = (40.7128, -74.006)  # New York
        vps3_location = (1.3521, 103.8198)  # Singapore

        hostname = urlparse(file_url).hostname
        file_ip = socket.gethostbyname(hostname)
        res = DbIpCity.get(file_ip, api_key="free")
        file_location = (res.latitude, res.longitude)

        vps1_distance = geodesic(vps1_location, file_location).km
        vps2_distance = geodesic(vps2_location, file_location).km
        vps3_distance = geodesic(vps3_location, file_location).km

        if vps1_distance <= vps2_distance and vps1_distance <= vps3_distance:
            closest_vps = '64.226.112.111'  # Frankfurt
        elif vps2_distance <= vps1_distance and vps2_distance <= vps3_distance:
            closest_vps = '165.22.8.234'  # NY
        else:
            closest_vps = '159.89.204.189'  # Singapore

        data = requests.post(f'http://{closest_vps}/upload', data={'file_url': file_url}).json()
        return render_template('result.html', data=data)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
