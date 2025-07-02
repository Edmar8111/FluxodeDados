from flask import Flask
from login_with_register import bp

app=Flask(__name__)

app.register_blueprint(bp)


if '__main__'==__name__:
    app.run(debug=True, host='127.0.0.1')