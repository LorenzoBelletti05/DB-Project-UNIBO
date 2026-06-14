from app import create_app

# Chiamiamo la funzione per inizializzare l'applicazione
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)