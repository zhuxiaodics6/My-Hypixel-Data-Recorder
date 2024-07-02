import hypixel
from hypixel import HypixelException
import asyncio
import sys
import time
from flask import Flask, render_template, redirect, request, send_from_directory
import threading
import matplotlib.pyplot as plt

app = Flask(__name__, static_url_path='', static_folder='templates', template_folder='templates')

if sys.platform:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

data_level = {}
data_time = {}
flag = {}
stats = []

async def getstats(username):
    global data_level,flag,data_time
    client = hypixel.Client('68335a8f-9636-48bb-8bb6-6b8164db40e2')
    async with client:
        data_time[username] = []
        data_level[username] = []
        while flag[username]:
            try:
                player = await client.player(username)
                f = open(f'log/player_{username}.log','a')
                print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} [{player.bedwars.level}*] [{player.rank}] {player.name}')
                f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} [{player.bedwars.level}*] [{player.rank}] {player.name}\n')
                f.close
                data_time[username] = data_time[username]+[time.strftime("%m-%d %H:%M", time.localtime())]
                data_level[username] = data_level[username]+[player.bedwars.level]
                print(data_time[username],data_level[username])
                time.sleep(5)
            except HypixelException as error:
                print(error)
def st(name):
    asyncio.run(getstats(name))

@app.route('/start', methods=['GET'])
def start():
    global flag, stats
    name = request.args.get('username')
    if name not in stats:
        stats.append(name)
        flag[name] = 1
        thread = threading.Thread(target=st,args=(name,))
        thread.start()
    return redirect('/info')

@app.route('/stop', methods=['GET'])
def stop():
    global flag, stats
    name = request.args.get('username')
    if name in stats:
        stats.remove(name)
        flag[name] = 0
    return redirect('/info')

@app.route('/info', methods=['GET'])
def info():
    global flag, stats
    return stats

@app.route('/pic', methods=['GET'])
def pic():
    global stats, data_level, data_time
    name = request.args.get('username')
    if name in stats:
        x_axis_data = data_time[name][-20:]
        print(x_axis_data)
        y_axis_data = data_level[name][-20:]
        print(y_axis_data)
        plt.plot(x_axis_data, y_axis_data, 'b*--', alpha=0.5, linewidth=1, label='acc')
        plt.title(name)
        plt.xticks(rotation=20)
        plt.xlabel('time')
        plt.ylabel('level')
        plt.savefig(f'templates/{name}.jpg')
        plt.close()
    return send_from_directory(app.static_folder, f'{name}.jpg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=1)