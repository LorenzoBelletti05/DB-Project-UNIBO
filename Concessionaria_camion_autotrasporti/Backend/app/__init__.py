from flask import Flask

def create_app():
    app = Flask(__name__, 
                template_folder='../../GUI/templates', 
                static_folder='../../GUI/static')
    
    #Line to make the login work
    app.config['SECRET_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im54bmN1eWZyZ3ZxYnJxZHZnb3lhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDIzOTA0OSwiZXhwIjoyMDk1ODE1MDQ5fQ.cT1m9O4LXsONLFd-7orV3F3nv5lKIoxSZGovzGqTmh0'
    
    from .routes import main
    app.register_blueprint(main)
    
    return app