import requests
import random
import string
import time
import urllib3
from urllib.parse import urljoin
import re

# Desactivar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CodeGenerator:
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
        """Obtener datos iniciales"""
        try:
            response = self.session.get(
                self.base_url,
                headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
            )
            response.raise_for_status()
            
            visit_id = re.search(r'name="_visit"\s+content="([^"]+)"', response.text)
            csrf_token = re.search(r'name="_token"\s+content="([^"]+)"', response.text)
            
            if not visit_id or not csrf_token:
                print("Error: No se pudieron extraer los datos necesarios")
                return None, None
                
            return visit_id.group(1), csrf_token.group(1)
            
        except Exception as e:
            print(f"Error inicial: {e}")
            return None, None

    def generate_random_email(self):
        """Generar email aleatorio"""
        return f"bot_{random.getrandbits(64)}@example.com"

    def submit_form(self):
        """Enviar formulario y obtener código"""
        try:
            visit_id, csrf_token = self.get_initial_data()
            if not all([visit_id, csrf_token]):
                return None

            response = self.session.post(
                urljoin(self.base_url, 'play/main'),
                data={
                    '_token': csrf_token,
                    'email': self.generate_random_email(),
                    'pack-code': random.choice(self.cities),
                    'policy1': '1',
                    'policy': '1',
                    'visit_id': visit_id
                }
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('exchange_code')
                
        except Exception as e:
            print(f"Error en la petición: {e}")
        return None

    def generate_codes(self, count=1):
        """Generar múltiples códigos con sus URLs"""
        urls = []
        for i in range(1, count + 1):
            print(f"\n--- Intento {i}/{count} ---")
            if code := self.submit_form():
                url = f"https://4d1c5188-c5d1-473e-9128-a00f91a677ac.playmo.es/?pl-exchange-code={code}&pl-prize=patatas"
                print(f"✅ Código: {code}")
                print(f"🔗 URL: {url}")
                urls.append(url)
            else:
                print("❌ Fallo al generar código")
        return urls

def save_urls_to_file(urls, filename='patatas.txt'):
    """Guardar URLs en un archivo, una por línea"""
    with open(filename, 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(f"{url}\n")
    print(f"\n✅ URLs guardadas en {filename}")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    print("Generador de códigos - Iniciando...\n")
    
    try:
        num_codes = int(input("¿Cuántos códigos quieres generar? "))
        if num_codes <= 0:
            print("Por favor, introduce un número positivo")
        else:
            urls = CodeGenerator().generate_codes(num_codes)
            
            if urls:
                print("\n🎉 Resultados:")
                for i, url in enumerate(urls, 1):
                    code = url.split('=')[1].split('&')[0]
                    print(f"\n{i}. Código: {code}")
                    print(f"   URL: {url}")
                
                # Guardar URLs en archivo
                save_urls_to_file(urls)
            else:
                print("\n❌ No se generaron códigos.")
                
    except ValueError:
        print("Por favor, introduce un número válido")
    except KeyboardInterrupt:
        print("\nOperación cancelada")
    except Exception as e:
        print(f"\nError: {e}")