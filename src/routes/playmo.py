from flask import Blueprint, request, jsonify
import requests
import random
import json
import urllib3
import time

# Desactivar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Crear blueprint
playmo_bp = Blueprint('playmo', __name__)

class PlaymoCodeGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        
        # Headers base para las solicitudes
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        self.promotion_id = "4d1c5188-c5d1-473e-9128-a00f91a677ac"
        self.base_url = f"https://{self.promotion_id}.playmo.es"
        
    def generate_random_email(self):
        """Generar email aleatorio"""
        timestamp = int(time.time() * 1000)  # Equivalente a Date.now() en JS
        return f"bot+{timestamp}@example.com"
    
    def generate_code(self, email, promo_type="patatas"):
        """
        Generar un código individual siguiendo exactamente el flujo del JavaScript que funciona
        """
        try:
            # Configurar headers para esta sesión
            self.session.headers.update(self.headers)
            self.session.headers.update({
                'Origin': self.base_url,
                'Referer': f"{self.base_url}/"
            })
            
            print(f"📧 Email configurado: {email}")
            print("🎯 Iniciando generación de código...")
            
            # Paso 1: POST /play/main (equivalente a Playmo.Ajax.main())
            form_data = {
                'email': email,
                'pack-code': 'SANTANDER',
                'policy[]': '1',
                'visit_id': str(random.randint(200000, 300000)),
                'extraData': '{"hash":"","query":{},"custom":{}}'
            }
            
            response1 = self.session.post(
                f"{self.base_url}/play/main",
                files={key: (None, value) for key, value in form_data.items()},
                verify=False
            )
            
            if response1.status_code != 200:
                print(f"❌ Error en paso 1: {response1.status_code}")
                return None
                
            data1 = response1.json()
            exchange_code = data1.get('exchange_code')
            play_id = data1.get('playId')
            prize_name = data1.get('prize', {}).get('name', 'Unknown')
            winner = data1.get('winner', False)
            
            if not exchange_code or not play_id:
                print("❌ No se pudo obtener exchange_code o playId")
                return None
            
            print("✅ Paso 1 completado - Código generado:")
            print(f"   Winner: {winner}")
            print(f"   Exchange Code: {exchange_code}")
            print(f"   Prize Name: {prize_name}")
            print(f"   Play ID: {play_id}")
            
            # Paso 2: POST /confirm-play (CRÍTICO para enviar el email)
            print("📨 Paso 2: Confirmando play para enviar email...")
            
            confirm_data = f"playId={play_id}"
            
            self.session.headers.update({
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            })
            
            response2 = self.session.post(
                f"{self.base_url}/confirm-play",
                data=confirm_data,
                verify=False
            )
            
            if response2.status_code != 200:
                print(f"❌ Error en confirmación: {response2.status_code}")
                return None
            
            try:
                confirm_result = response2.json()
                print(f"✅ Confirmación exitosa: {confirm_result}")
                
                if confirm_result.get('status') == 'ok':
                    print("🎉 EMAIL ENVIADO CORRECTAMENTE")
                else:
                    print(f"⚠️ Respuesta inesperada en confirmación: {confirm_result}")
            except json.JSONDecodeError:
                print("⚠️ Respuesta de confirmación no es JSON válido")
            
            # Resumen final
            print("🎉 RESUMEN FINAL:")
            print(f"   Código generado: {exchange_code}")
            print(f"   Email usado: {email}")
            print(f"   Premio: {prize_name}")
            print(f"   URL para patatas: {self.base_url}/?pl-exchange-code={exchange_code}&pl-prize=patatas")
            print(f"   URL para bebidas: {self.base_url}/?pl-exchange-code={exchange_code}&pl-prize=bebida")
            
            return {
                'exchange_code': exchange_code,
                'prize_name': prize_name,
                'winner': winner,
                'play_id': play_id,
                'email_sent': True
            }
            
        except Exception as e:
            print(f"❌ Error en la generación: {e}")
            return None

    def generate_code_with_prize_preference(self, email, preferred_prize="bebida", max_attempts=15):
        """
        Generar códigos hasta conseguir el premio preferido
        """
        print(f"🎯 Buscando premio de {preferred_prize.upper()}...")
        print(f"📊 Máximo {max_attempts} intentos")
        
        packs = ['SANTANDER', 'VALLADOLID', 'SEVILLA']
        
        for attempt in range(1, max_attempts + 1):
            print(f"\n🔄 INTENTO {attempt}/{max_attempts}")
            
            # Email único para cada intento
            timestamp = int(time.time() * 1000) + attempt
            attempt_email = f"{preferred_prize}{attempt}+{timestamp}@example.com"
            
            # Rotar entre diferentes packs
            selected_pack = packs[(attempt - 1) % len(packs)]
            
            try:
                # Configurar headers
                self.session.headers.update(self.headers)
                self.session.headers.update({
                    'Origin': self.base_url,
                    'Referer': f"{self.base_url}/"
                })
                
                print(f"📧 Email: {attempt_email}")
                print(f"📦 Pack: {selected_pack}")
                
                # Paso 1: POST /play/main
                form_data = {
                    'email': attempt_email,
                    'pack-code': selected_pack,
                    'policy[]': '1',
                    'visit_id': str(random.randint(200000, 300000)),
                    'extraData': '{"hash":"","query":{},"custom":{}}'
                }
                
                response1 = self.session.post(
                    f"{self.base_url}/play/main",
                    files={key: (None, value) for key, value in form_data.items()},
                    verify=False
                )
                
                if response1.status_code != 200:
                    print(f"❌ Error en intento {attempt}: {response1.status_code}")
                    time.sleep(2)
                    continue
                    
                data1 = response1.json()
                exchange_code = data1.get('exchange_code')
                play_id = data1.get('playId')
                prize_name = data1.get('prize', {}).get('name', 'Unknown')
                
                print(f"🎁 Premio obtenido: {prize_name}")
                print(f"🔢 Código: {exchange_code}")
                
                # Verificar si es el premio que buscamos
                if preferred_prize.lower() in prize_name.lower() or \
                   'bebida' in prize_name.lower() or \
                   'drink' in prize_name.lower() or \
                   'refresco' in prize_name.lower():
                    
                    print("🎉 ¡ÉXITO! Premio deseado encontrado")
                    
                    # Confirmar el play para enviar el email
                    print("📨 Confirmando play para enviar email...")
                    
                    confirm_data = f"playId={play_id}"
                    self.session.headers.update({
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                    })
                    
                    response2 = self.session.post(
                        f"{self.base_url}/confirm-play",
                        data=confirm_data,
                        verify=False
                    )
                    
                    if response2.status_code == 200:
                        confirm_result = response2.json()
                        if confirm_result.get('status') == 'ok':
                            print(f"✅ EMAIL DE {preferred_prize.upper()} ENVIADO CORRECTAMENTE")
                    
                    return {
                        'exchange_code': exchange_code,
                        'prize_name': prize_name,
                        'attempt': attempt,
                        'email_used': attempt_email,
                        'pack_used': selected_pack,
                        'email_sent': True
                    }
                else:
                    print(f"❌ Premio no deseado: {prize_name}")
                    time.sleep(1)  # Pausa entre intentos
                    
            except Exception as e:
                print(f"❌ Error en intento {attempt}: {e}")
                time.sleep(2)
        
        print(f"\n😞 No se pudo conseguir premio de {preferred_prize} en {max_attempts} intentos")
        return None

# Instancia global del generador
generator = PlaymoCodeGenerator()

@playmo_bp.route('/generate_code', methods=['POST'])
def generate_code():
    """Endpoint para generar un código individual"""
    try:
        data = request.get_json()
        
        # Validar datos de entrada
        promo_type = data.get('promoType')
        email_option = data.get('emailOption')
        custom_email = data.get('customEmail')
        
        if not promo_type or promo_type not in ['patatas', 'bebida']:
            return jsonify({'error': 'Tipo de promoción inválido.'}), 400
        
        if not email_option or email_option not in ['random', 'custom']:
            return jsonify({'error': 'Opción de email inválida.'}), 400
        
        # Determinar el email a usar
        if email_option == 'custom':
            if not custom_email or '@' not in custom_email:
                return jsonify({'error': 'Correo electrónico personalizado inválido.'}), 400
            email = custom_email
        else:
            email = generator.generate_random_email()
        
        # Generar código usando el método corregido
        result = generator.generate_code(email, promo_type)
        
        if result:
            url = f"https://{generator.promotion_id}.playmo.es/?pl-exchange-code={result['exchange_code']}&pl-prize={promo_type}"
            return jsonify({
                'success': True,
                'code': result['exchange_code'],
                'url': url,
                'prize_name': result['prize_name'],
                'email_sent': result['email_sent']
            })
        else:
            return jsonify({'error': 'Error al generar el código.'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

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
        
        if not email_option or email_option not in ['random', 'custom']:
            return jsonify({'error': 'Opción de email inválida.'}), 400
        
        if email_option == 'custom' and (not custom_email or '@' not in custom_email):
            return jsonify({'error': 'Correo electrónico personalizado inválido.'}), 400
        
        # Generar múltiples códigos
        results = []
        errors = []
        
        for i in range(num_codes):
            # Determinar el email a usar
            if email_option == 'custom':
                email = custom_email
            else:
                email = generator.generate_random_email()
            
            # Generar código usando el método corregido
            result = generator.generate_code(email, promo_type)
            
            if result:
                url = f"https://{generator.promotion_id}.playmo.es/?pl-exchange-code={result['exchange_code']}&pl-prize={promo_type}"
                results.append({
                    'code': result['exchange_code'],
                    'url': url,
                    'index': i + 1,
                    'prize_name': result['prize_name'],
                    'email_sent': result['email_sent']
                })
            else:
                errors.append({
                    'index': i + 1,
                    'error': 'Error al generar el código'
                })
            
            # Pausa entre generaciones para no saturar el servidor
            if i < num_codes - 1:
                time.sleep(1)
        
        return jsonify({
            'success': True,
            'results': results,
            'errors': errors,
            'total_requested': num_codes,
            'total_generated': len(results),
            'total_failed': len(errors)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@playmo_bp.route('/generate_with_preference', methods=['POST'])
def generate_with_preference():
    """Endpoint para generar códigos con preferencia de premio"""
    try:
        data = request.get_json()
        
        preferred_prize = data.get('preferredPrize', 'bebida')
        max_attempts = data.get('maxAttempts', 15)
        
        if max_attempts > 20:
            max_attempts = 20  # Límite de seguridad
        
        result = generator.generate_code_with_prize_preference(
            email=None,  # Se genera automáticamente
            preferred_prize=preferred_prize,
            max_attempts=max_attempts
        )
        
        if result:
            url = f"https://{generator.promotion_id}.playmo.es/?pl-exchange-code={result['exchange_code']}&pl-prize={preferred_prize}"
            return jsonify({
                'success': True,
                'code': result['exchange_code'],
                'url': url,
                'prize_name': result['prize_name'],
                'attempts_needed': result['attempt'],
                'email_used': result['email_used'],
                'pack_used': result['pack_used'],
                'email_sent': result['email_sent']
            })
        else:
            return jsonify({
                'success': False,
                'error': f'No se pudo conseguir premio de {preferred_prize} en {max_attempts} intentos'
            }), 404
            
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
