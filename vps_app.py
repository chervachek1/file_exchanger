import time
from werkzeug.utils import secure_filename
import requests
from flask import Flask, request, url_for, send_file
import os
import asyncio
import aiohttp
import shutil

app = Flask(__name__)


@app.route('/upload', methods=['POST'])
def upload_file():
    vps = {
        '68.183.221.123': 'VPS1 Frankfurt',
        '157.245.131.73': 'VPS2 New York',
        '146.190.100.196': 'VPS3 Singapore',
    }

    start_time = time.time()
    file_url = request.form.get('file_url')
    filename = secure_filename(file_url.split('/')[-1])
    with requests.get(file_url, stream=True) as response:
        with open(f'files/{filename}', 'wb') as file:
            shutil.copyfileobj(response.raw, file, length=16*1024*1024)
    end_time = time.time()
    duration = round(end_time - start_time, 2)
    file_size = os.path.getsize(os.path.join('files', filename))
    file_link = url_for('download_file', filename=filename)

    current_vps = request.host.split(':')[0]
    data = [{
        'vps': vps[current_vps],
        'vps_ip': current_vps,
        'duration': duration,
        'end_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)),
        'file_size': file_size,
        'file_link': file_link,
    }]

    async def replicate_concurrently(current_vps, file_link, vps):
        tasks = []
        async with aiohttp.ClientSession() as session:
            for key, val in vps.items():
                if key != current_vps:
                    task = asyncio.ensure_future(
                        session.post(f'http://{key}/replicate', data={'file_url': f'http://{current_vps}{file_link}'}))
                    tasks.append(task)
            responses = await asyncio.gather(*tasks)
            for response in responses:
                vps_info = await response.json()
                vps_info.update({'vps': vps[vps_info['vps_ip']]})
                data.append(vps_info)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(replicate_concurrently(current_vps, file_link, vps))
    loop.close()

    return data


@app.route('/replicate', methods=['POST'])
def replicate():
    start_time = time.time()
    file_url = request.form.get('file_url')
    filename = secure_filename(file_url.split('/')[-1])
    with requests.get(file_url, stream=True) as response:
        with open(f'files/{filename}', 'wb') as file:
            shutil.copyfileobj(response.raw, file, length=16*1024*1024)
    end_time = time.time()
    duration = round(end_time - start_time, 2)
    file_size = os.path.getsize(os.path.join('files', filename))
    file_link = url_for('download_file', filename=filename)
    current_vps = request.host.split(':')[0]
    return {
        'duration': duration,
        'end_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)),
        'file_size': file_size,
        'file_link': file_link,
        'vps_ip': current_vps,
    }


@app.route('/<filename>')
def download_file(filename):
    path = f'files/{filename}'
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run(host='68.183.221.123', port=80)
