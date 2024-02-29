from flask import Blueprint, jsonify

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/")
def index():
    return jsonify({"message": "API funcionando!"})

@api.route("/usuarios")
def get_usuarios():
    # Retorna uma lista de usuários do banco de dados
    return jsonify([{"nome": "Usuario 1"}, {"nome": "Usuario 2"}])