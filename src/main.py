import os
import sys
from flask import Flask
from flask_cors import CORS

# Añadir el directorio src al path para importaciones relativas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar el blueprint de playmo
from routes.playmo import playmo_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui' # Cambia esto por una clave segura

# Habilitar CORS para todas las rutas
CORS(app)

# Registrar blueprints
app.register_blueprint(playmo_bp, url_prefix='/api')

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)
