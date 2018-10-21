from flask import Flask

app = Flask(__name__)

from .resources import create_excel, get_excel
from .views import index


def runserver(port=32067, **kwargs):
    app.run(
        port=port,
        **kwargs
    )
