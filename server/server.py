from flask import Flask, request, jsonify, send_file
import sqlite3

app = Flask(__name__)
data = {}
id_counter = 1
now_working = []
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()


def save(file, id):
    name = f"{id}.png"
    k = id
    now_working.append(k)
    file.save(name)
    now_working.remove(k)


@app.route('/check_connection', methods=['GET'])
def check_connection():
    return jsonify({"message": "True"})


@app.route('/api', methods=['GET'])
def api():
    global id_counter
    if 'id' in request.args:
        if request.args['id'] == '0':
            # регистрируем пользователя
            new_id = id_counter
            id_counter += 1
            data[new_id] = {}
            data[new_id]["os"] = request.args['os']
            data[new_id]["coords"] = (100, 100)
            data[new_id]["is_clicked"] = False
            data[new_id]["data"] = []
            data[new_id]["display"] = [1920, 1080]
            returned = {"message": "ID", 'id': new_id}
            return jsonify(returned)
    elif 'get_for_id' in request.args and request.args['get_for_id'].isdigit() and int(request.args['get_for_id']) > 0:
        # запрос на передвижение и клики
        d = {"m": True}
        d["coords"] = data[int(request.args['get_for_id'])]["coords"]
        d["is_clicked"] = data[int(request.args['get_for_id'])]["is_clicked"]
        d["data"] = data[int(request.args['get_for_id'])]["data"].copy()
        d["display"] = data[int(request.args['get_for_id'])]["display"]
        data[int(request.args['get_for_id'])]["data"] = []
        return jsonify(d)
    elif "get_image" in request.args:
        with open(f'{request.args["get_image"]}.png', 'rb') as f:
            img_data = f.read().decode('utf-8')
        returned = {'message': 'Returned', 'img': img_data}
        return jsonify(returned)
    returned = {'message': 'Invalid request'}
    return jsonify(returned)


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    name = file.filename
    download_id = request.args["id"]
    while download_id in now_working:
        pass
    save(file, download_id)
    return 'Файл успешно загружен'


@app.route('/test', methods=['POST'])
def test():
    args = request.get_json()
    return jsonify(args)


@app.route('/moving', methods=['POST'])
def moving():
    # сохраняем передвижение и клики мыши
    args = request.get_json(force=True)
    coords = args["coords"]
    is_clicked = bool(int(args["is_clicked"]))
    data_about_buttons = args["data"]
    display = args["display"]
    data[int(args['id'])]["coords"] = coords
    data[int(args['id'])]["is_clicked"] = is_clicked
    data[int(args['id'])]["data"] += data_about_buttons
    data[int(args['id'])]["display"] = display
    returned = {'message': 'Saved', "data": data[int(args['id'])]}
    return jsonify(returned)


@app.route('/download')
def download_file():
    path = f'../{request.args["id"]}.png'
    download_id = request.args["id"]
    while download_id in now_working:
        pass
    now_working.append(download_id)
    file = send_file(path, as_attachment=True)
    now_working.remove(download_id)
    return file


@app.route('/get_data', methods=['GET'])
def get_data():
    returned = {}
    for e in data.keys():
        print(e)
        returned[int(e)] = data[e]["os"]
    return jsonify(returned)


@app.route("/check_login", methods=["GET"])
def check_login():
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (request.args["username"], request.args["password"]))
    if c.fetchone() is not None:
        return jsonify({"res": True})
    else:
        return jsonify({"res": False})


if __name__ == '__main__':
    print("Starting server")
    app.run(debug=True)