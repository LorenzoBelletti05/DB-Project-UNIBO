import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Carica le variabili dal file .env
load_dotenv()

# Prendi la stringa di connessione in modo sicuro
DATABASE_URI = os.getenv("DATABASE_URL")

def get_db_connection():
    """Crea e restituisce una connessione a Supabase."""
    if not DATABASE_URI:
        raise ValueError("Errore critico: DATABASE_URL non trovato nel file .env!")
    
    try:
        # Ci connettiamo al database in cloud
        conn = psycopg2.connect(DATABASE_URI)
        
        # Restituisce i risultati come dizionari (es. riga['targa'])
        conn.cursor_factory = RealDictCursor 
        return conn
    except psycopg2.Error as e:
        print(f"Errore di connessione al database: {e}")
        return None