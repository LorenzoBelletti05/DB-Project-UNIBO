# Backend/app/__init__.py
import os
from flask import Flask

# Trova il percorso assoluto di questa cartella (Backend/app)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Spostati indietro di due livelli ed entra nella cartella GUI
template_dir = os.path.abspath(os.path.join(current_dir, '../../GUI/templates'))
static_dir = os.path.abspath(os.path.join(current_dir, '../../GUI/static'))

# Inizializza Flask dicendogli esattamente dove sono i file grafici
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Importa le rotte
from app import routes