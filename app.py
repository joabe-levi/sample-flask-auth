import bcrypt
from flask import Flask, jsonify, request
from database import db
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

# Precisa fazer o import do User pra migrar o banco
from models.user import User

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/flask-crud'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username and password:
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            print(current_user.is_authenticated)
                
            return jsonify({'message': 'sucesso'}), 200
        
        return jsonify({'message': 'Username or password is incorrect'}), 400
        
    return jsonify({'message': 'Missing username or password'}), 400


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Success logout'}), 200


@app.route('/user', methods=['POST'])
@login_required
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400
    
    hashed_pw = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
    
    user = User(username=username, password=hashed_pw, email=email, role='user')
    user.save()
    
    return jsonify({'message': 'Success'}), 200


@app.route('/user/<int:id>/', methods=['GET'])
@login_required
def read_user(id):
    user = User.query.get(id)
    
    if user:
        return jsonify({'id': user.id, 'username': user.username, 'email': user.email}), 200
    
    return jsonify({'message': 'User not found'}), 404


@app.route('/user/update/<int:id>/', methods=['PUT'])
@login_required
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    if id != current_user.id and current_user.role == 'user':
        return jsonify({'message': "You can't update another user"}), 403
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    user.username = username
    user.password = password
    user.email = email
    user.save()
    
    return jsonify({'message': f'User ({user.username}) updated successfully'}), 200


@app.route('/user/delete/<int:id>/', methods=['DELETE'])
@login_required
def delete_user(id):
    user = User.query.get(id)
    
    if current_user.role != 'admin':
        return jsonify({'message': "You can't delete another user"}), 403
    
    if user and user == current_user:
        return jsonify({'message': "You can't delete yourself"}), 400
    
    if user:
        user.delete()
        return jsonify({'message': 'Usuário deletado com sucesso.'}), 200
    
    return jsonify({'message': 'User not found'}), 204


@app.route('/hello_world', methods=['GET'])
def hello_world():
    return 'Hello World'


if __name__ == '__main__':
    app.run(debug=True)
