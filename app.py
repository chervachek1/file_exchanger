import time
from flask import Flask, render_template, request, redirect, after_this_request, send_file, url_for
import requests
from geopy.distance import geodesic
import socket
from urllib.parse import urlparse
from ip2geotools.databases.noncommercial import DbIpCity

app = Flask(__name__)

vps1_location = (50.121, 8.4966)  # Frankfurt
vps2_location = (40.7128, -74.006)  # New York
vps3_location = (1.290270, 103.851959)  # Singapore


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file_link = request.form['file_url']

        hostname = urlparse(file_link).hostname
        file_ip = socket.gethostbyname(hostname)
        res = DbIpCity.get(file_ip, api_key="free")
        file_location = (res.latitude, res.longitude)

        vps1_distance = geodesic(vps1_location, file_location).km
        vps2_distance = geodesic(vps2_location, file_location).km
        vps3_distance = geodesic(vps3_location, file_location).km

        if vps1_distance <= vps2_distance and vps1_distance <= vps3_distance:
            closest_vps = '68.183.221.123'  # Frankfurt
        elif vps2_distance <= vps1_distance and vps2_distance <= vps3_distance:
            closest_vps = '157.245.131.73'  # NY
        else:
            closest_vps = '146.190.100.196'  # Singapore
        data = requests.post(f'http://{closest_vps}/upload', data={'file_url': file_link}).json()
        return render_template('result.html', data=data)
    return render_template('index.html')


@app.route('/download/<filename>')
def download_file(filename):
    user_ip = request.remote_addr
    res = DbIpCity.get(user_ip, api_key="free")
    user_location = (res.latitude, res.longitude)

    vps1_distance = geodesic(vps1_location, user_location).km
    vps2_distance = geodesic(vps2_location, user_location).km
    vps3_distance = geodesic(vps3_location, user_location).km
    print(vps1_distance, vps2_distance, vps3_distance)

    if vps1_distance <= vps2_distance and vps1_distance <= vps3_distance:
        closest_vps = '68.183.221.123'  # Frankfurt
        vps_name = 'VPS1 Frankfurt'
    elif vps2_distance <= vps1_distance and vps2_distance <= vps3_distance:
        closest_vps = '157.245.131.73'  # NY
        vps_name = 'VPS2 New York'
    else:
        closest_vps = '146.190.100.196'  # Singapore
        vps_name = 'VPS3 Singapore'

    start_time = time.time()
    response = requests.get(f'http://{closest_vps}/{filename}')
    with open(f'files/{filename}', 'wb') as file:
        file.write(response.content)
    end_time = time.time()
    duration = round(end_time - start_time, 2)
    data = {
        'vps': vps_name,
        'vps_ip': closest_vps,
        'duration': duration,
        'end_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)),
        'file_url': url_for('get_file', filename=filename)
    }
    return render_template('download_result.html', data=data)


@app.route('/<filename>')
def get_file(filename):
    path = f'files/{filename}'
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
