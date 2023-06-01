import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from .ocr import FlaskOCR
from .drive import FlaskDrive

app = Flask(__name__)
# # https://stackoverflow.com/questions/10018679/python-find-closest-string-from-a-list-to-another-string
# # Tesseractt Windows: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe

app.config['SECRET_KEY'] ='dc1e5657c2375d4037942585ea2cb3a2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
LOCAL_IMAGE_FOLDER = os.path.join('static', 'report_pics')
db = SQLAlchemy(app)


bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

ocr_tool = FlaskOCR()

gcp_secret= os.path.join(app.root_path, 'static', 'gcp_cloud_secret.json')
drive_tool = FlaskDrive(gcp_secret)

if not os.path.exists(os.path.join(app.root_path, LOCAL_IMAGE_FOLDER)):
    os.makedirs(os.path.join(app.root_path, LOCAL_IMAGE_FOLDER))

# a = drive_tool.create_folder('for_custom_demo')

# demo_img = os.path.join(app.root_path, '..', 'demo_imgs', 'table1.jpg')
# a = drive_tool.upload_file(demo_img)
# a = ocr_tool.get_info_str(demo_img)
# print(a)
# print('cccc')


from flaskapp import routes
