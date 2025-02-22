import os
from flask import Flask, send_from_directory
from app import create_app

app = create_app()

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(app.static_folder, 'assets'), filename)

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=8080)