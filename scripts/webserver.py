import flask

import frames_io_handler as io

app = flask.Flask('thermappmd')
app.config['SECRET_KEY'] = 'thermapp'


FRAME_PATH = '/home/debian/opgal/dump'

@app.route('/')
def home():
    msg = 'To get the last frame, fetch: <a href="{0}">{0}</a>'.format(flask.url_for('last_frame'))
    return msg

@app.route('/last_frame')
def last_frame():
    last_frame = io.get_last_frame(FRAME_PATH)
    print(last_frame)
    return flask.send_file(last_frame)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)



