from app import app

if __name__ == '__main__':
    print("🚀 Avvio del server Backend in corso...")
    print("🌐 Vai su http://127.0.0.1:5000 per vedere la tua Dashboard")
    # debug=True ti permette di vedere le modifiche al codice senza dover riavviare il server ogni volta
    app.run(debug=True, port=5000)