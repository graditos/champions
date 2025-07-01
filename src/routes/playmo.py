from flask import Blueprint, request, jsonify
import requests
import random
import urllib3
from urllib.parse import urljoin
import re

# Desactivar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

playmo_bp = Blueprint('playmo', __name__)

class PlaymoCodeGenerator:
    def __init__(self):
        self.base_url = "https://4d1c5188-c5d1-473e-9128-a00f91a677ac.playmo.es/"
        self.session = requests.Session()
        self.cities = ['SANTANDER', 'VALLADOLID', 'SEVILLA']
        self.session.verify = False
        
        # Configurar headers
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Origin': 'https://4d1c5188-c5d1-473e-9128-a00f91a677ac.playmo.es',
            'Referer': self.base_url,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }

    def get_initial_data(self):
        """Obtener datos iniciales (visit_id y _token)"""
        try:
            response = self.session.get(
                self.base_url,
                headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
            )
            response.raise_for_status()
            
            visit_id = re.search(r'name="_visit"\s+content="([^"]+)"', response.text)
            csrf_token = re.search(r'name="_token"\s+content="([^"]+)"', response.text)
            
            if not visit_id or not csrf_token:
                return None, None
                
            return visit_id.group(1), csrf_token.group(1)
            
        except Exception as e:
            print(f"Error inicial: {e}")
            return None, None

    def generate_random_email(self):
        """Generar email aleatorio"""
        return f"bot_{random.getrandbits(64)}@example.com"

    def submit_form_and_get_code(self, email_to_use, promo_type):
        """Enviar formulario y obtener código y URL completa"""
        try:
            visit_id, csrf_token = self.get_initial_data()
            if not all([visit_id, csrf_token]):
                return None, None, "No se pudieron obtener datos iniciales."

            response = self.session.post(
                urljoin(self.base_url, 'play/main'),
                data={
                    '_token': csrf_token,
                    'email': email_to_use,
                    'pack-code': random.choice(self.cities),
                    'policy1': '1',
                    'policy': '1',
                    'visit_id': visit_id
                }
            )

            if response.status_code == 200:
                data = response.json()
                exchange_code = data.get('exchange_code')
                if exchange_code:
                    # Construir la URL con el tipo de promoción correcto
                    final_url = f"https://4d1c5188-c5d1-473e-9128-a00f91a677ac.playmo.es/?pl-exchange-code={exchange_code}&pl-prize={promo_type}"
                    return exchange_code, final_url, None
                else:
                    return None, None, "No se recibió un código de intercambio."
            else:
                return None, None, f"Error en la respuesta del servidor: {response.status_code}"

        except requests.exceptions.RequestException as e:
            return None, None, f"Error de red: {e}"
        except Exception as e:
            return None, None, f"Error inesperado: {e}"

# Instancia global del generador
generator = PlaymoCodeGenerator()

@playmo_bp.route('/generate_code', methods=['POST'])
def generate_code():
    """Endpoint para generar un código individual"""
    try:
        data = request.get_json()
        print(f"DEBUG: Datos recibidos: {data}")
        
        # Validar datos de entrada
        promo_type = data.get('promoType')
        email_option = data.get('emailOption')
        custom_email = data.get('customEmail')
        
        print(f"DEBUG: promo_type={promo_type}, email_option={email_option}, custom_email={custom_email}")

        if not promo_type or promo_type not in ['patatas', 'bebida']:
            return jsonify({'error': 'Tipo de promoción inválido.'}), 400

        # Determinar qué email usar
        email_to_use = ""
        if email_option == 'random':
            email_to_use = generator.generate_random_email()
        elif email_option == 'custom':
            if not custom_email or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', custom_email):
                return jsonify({'error': 'Correo electrónico personalizado inválido.'}), 400
            email_to_use = custom_email
        else:
            return jsonify({'error': 'Opción de correo electrónico inválida.'}), 400

        # Generar código
        code, url, error = generator.submit_form_and_get_code(email_to_use, promo_type)

        if code and url:
            return jsonify({
                'success': True,
                'code': code,
                'url': url
            })
        else:
            return jsonify({
                'success': False,
                'error': error or 'Fallo al generar el código.'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500

@playmo_bp.route('/generate_multiple_codes', methods=['POST'])
def generate_multiple_codes():
    """Endpoint para generar múltiples códigos"""
    try:
        data = request.get_json()
        
        # Validar datos de entrada
        num_codes = data.get('numCodes')
        promo_type = data.get('promoType')
        email_option = data.get('emailOption')
        custom_email = data.get('customEmail')

        if not isinstance(num_codes, int) or num_codes <= 0 or num_codes > 50:
            return jsonify({'error': 'Número de códigos inválido (1-50).'}), 400

        if not promo_type or promo_type not in ['patatas', 'bebida']:
            return jsonify({'error': 'Tipo de promoción inválido.'}), 400

        # Determinar qué email usar
        email_to_use = ""
        if email_option == 'random':
            # Para múltiples códigos con email aleatorio, generar uno diferente para cada código
            pass  # Se generará en el bucle
        elif email_option == 'custom':
            if not custom_email or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', custom_email):
                return jsonify({'error': 'Correo electrónico personalizado inválido.'}), 400
            email_to_use = custom_email
        else:
            return jsonify({'error': 'Opción de correo electrónico inválida.'}), 400

        # Generar múltiples códigos
        results = []
        errors = []

        for i in range(num_codes):
            # Si es email aleatorio, generar uno nuevo para cada código
            if email_option == 'random':
                email_to_use = generator.generate_random_email()
            
            code, url, error = generator.submit_form_and_get_code(email_to_use, promo_type)
            
            if code and url:
                results.append({
                    'code': code,
                    'url': url,
                    'index': i + 1
                })
            else:
                errors.append({
                    'index': i + 1,
                    'error': error or 'Fallo al generar el código.'
                })

        return jsonify({
            'success': True,
            'results': results,
            'errors': errors,
            'total_requested': num_codes,
            'total_generated': len(results),
            'total_failed': len(errors)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500
