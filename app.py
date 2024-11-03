from flask import Flask
from datetime import timedelta
app_instance = Flask(__name__)

# Configure the SQLAlchemy database URI
app_instance.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app_instance.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app_instance.config['JWT_SECRET_KEY'] = 'my_jwt_secret_key'
app_instance.config['USERNAME'] = "UserName"
app_instance.config['PASSWORD'] = "UserSecret"
app_instance.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

with app_instance.app_context():
    import view

if __name__ == '__main__':
    app_instance.run(debug=True)