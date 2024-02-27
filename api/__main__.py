from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/v1/exemplo', methods=['GET'])
def get_exemplo():
    dados = {
        "nome": "Exemplo",
        "valor": 123
    }
    return jsonify(dados)

if __name__ == '__main__':
    app.run(debug=True)