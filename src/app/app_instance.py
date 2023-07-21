from flask import Flask
from ..constants.api_constants import TEMPLATES_FOLDER, STATIC_FOLDER

app = Flask(
    __name__,
    template_folder=TEMPLATES_FOLDER,
    static_folder=STATIC_FOLDER,
)
