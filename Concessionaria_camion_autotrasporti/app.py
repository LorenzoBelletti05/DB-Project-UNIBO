from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Benvenuto nel gestionale della Concessionaria!"

if __name__ == "__main__":
    app.run(debug=True)