import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env situato nella cartella genitore
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Credenziali Supabase mancanti. Controlla il file .env")

# Inizializza il client Supabase
supabase: Client = create_client(url, key)