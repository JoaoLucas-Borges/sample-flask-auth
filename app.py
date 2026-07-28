from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required


app = Flask (__name__)
app.config["SECRET_KEY"] = "Your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"


Login_Manager = LoginManager()


db.init_app(app)
Login_Manager.init_app(app)


# View login
Login_Manager.login_view = "login"


@Login_Manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/login", methods = ["POST"])
def login():
    data = request.json
    username = data.get("username") #Recebendo credenciais pelo corpo da requisição
    password = data.get("password")

    if username and password:
        #Login
        user = User.query.filter_by(username= username).first() # Buscamos no banco o primeiro usuário com esse username
        if user and user.password == password: # Verifica se o username foi encontrado e se a senha é igual a request
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Autenticacao realizada com sucesso!"})
    
    return jsonify({"message": "Credenciais inválidas"}), 400


@app.route("/logout", methods = ["GET"])
@login_required # Garante que só terão acesso ao logout quem está logado
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso!"})


@app.route("/user", methods = ["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User(username = username, password = password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message":"usuário cadastrado com sucesso!"})

    return jsonify({"message": "Dados inválidos!"}), 400


@app.route("/user/<int:id_user>", methods = ["GET"])
@login_required
def read_user(id_user):
    user = User.query.get(id_user)
    if user:
        return jsonify({"message": user.username})

    return jsonify({"message": "Usário não encontrado!"}), 404


@app.route("/user/<int:id_user>", methods = ["PUT"])
@login_required
def update_user(id_user):
    data = request.json
    user = User.query.get(id_user)

    if user and data.get("password"):
        user.password = data.get("password")
        db.session.commit()

        return jsonify({"message":f"Usuário {id_user} atualizado com sucesso!"})

    return jsonify({"message": "Usário não encontrado!"}), 404


@app.route("/user/<int:id_user>", methods = ["DELETE"])
@login_required
def delete_user(id_user):
    user = User.query.get(id_user)

    if id_user == current_user.id:
        return jsonify({"message":"Deleção não permitida!"}), 403 # Garante que o sistema será utilizável depois da deleção


    if user and id_user != current_user.id:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"Usuário {id_user} deletado com sucesso!"})

    return jsonify({"message": "Usário não encontrado!"}), 404


if __name__ == "__main__":
    app.run(debug=True)
