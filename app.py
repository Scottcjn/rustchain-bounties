from flask import Flask, render_template

app = Flask(__name__)

@app.route('/bridge/wrtc')
def bridge_wrtc():
    return render_template('bottube_templates/bridge_wrtc.html')

@app.route('/bridge/base')
def bridge_base():
    return render_template('bottube_templates/bridge_base.html')

if __name__ == '__main__':
    app.run()