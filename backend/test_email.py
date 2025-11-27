"""
Script de prueba para verificar el envío de correos con Namecheap
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_email_connection():
    """Prueba la conexión SMTP"""
    print("🔍 Probando conexión SMTP...")
    print(f"   Host: {os.getenv('SMTP_HOST')}")
    print(f"   Puerto: {os.getenv('SMTP_PORT')}")
    print(f"   Usuario: {os.getenv('SMTP_USER')}")
    print(f"   De: {os.getenv('EMAIL_FROM')}")
    print(f"   Para (copia): {os.getenv('EMAIL_NASSA')}")
    print()
    
    try:
        # Crear servidor SMTP
        server = smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT')))
        server.set_debuglevel(1)  # Ver detalles de la conexión
        server.starttls()
        
        # Autenticar
        print("\n🔐 Autenticando...")
        server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASS'))
        print("✅ Autenticación exitosa!")
        
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ Error en conexión: {str(e)}")
        return False

def send_test_email(destinatario: str):
    """Envía un correo de prueba"""
    print(f"\n📧 Enviando correo de prueba a: {destinatario}")
    
    try:
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = os.getenv('EMAIL_FROM')
        msg['To'] = destinatario
        msg['Subject'] = "Prueba de Configuración - NASSA Solar"
        
        # Cuerpo del mensaje
        body = """
        ¡Hola!
        
        Este es un correo de prueba para verificar la configuración del sistema de cotizaciones NASSA Solar.
        
        Si recibiste este correo, significa que la configuración de Namecheap Private Email está funcionando correctamente.
        
        Detalles de configuración:
        - Servidor SMTP: mail.privateemail.com
        - Puerto: 587
        - Remitente: comercial@nassasolar.com
        
        Saludos,
        Sistema de Cotizaciones NASSA Solar
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Enviar
        server = smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT')))
        server.starttls()
        server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASS'))
        
        # Enviar a destinatario principal
        text = msg.as_string()
        server.sendmail(os.getenv('EMAIL_FROM'), destinatario, text)
        
        # Enviar copia a EMAIL_NASSA
        if os.getenv('EMAIL_NASSA') and os.getenv('EMAIL_NASSA') != destinatario:
            print(f"📧 Enviando copia a: {os.getenv('EMAIL_NASSA')}")
            server.sendmail(os.getenv('EMAIL_FROM'), os.getenv('EMAIL_NASSA'), text)
        
        server.quit()
        
        print("✅ Correo enviado exitosamente!")
        print(f"   Destinatario: {destinatario}")
        if os.getenv('EMAIL_NASSA'):
            print(f"   Copia: {os.getenv('EMAIL_NASSA')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar correo: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("   PRUEBA DE CONFIGURACIÓN DE EMAIL - NASSA SOLAR")
    print("=" * 60)
    print()
    
    # Verificar variables de entorno
    if not all([os.getenv('SMTP_HOST'), os.getenv('SMTP_USER'), os.getenv('SMTP_PASS')]):
        print("❌ Error: Faltan variables de entorno en .env")
        exit(1)
    
    # Prueba 1: Conexión
    print("PRUEBA 1: Conexión SMTP")
    print("-" * 60)
    if not test_email_connection():
        print("\n❌ La prueba de conexión falló. Verifica las credenciales.")
        exit(1)
    
    # Prueba 2: Envío de correo
    print("\n" + "=" * 60)
    print("PRUEBA 2: Envío de Correo de Prueba")
    print("-" * 60)
    
    # Pedir correo de destino
    destino = input("\n📧 Ingresa el correo de destino para la prueba: ").strip()
    
    if not destino:
        destino = os.getenv('EMAIL_NASSA', 'nassasolar.comercial@outlook.com')
        print(f"   Usando destino por defecto: {destino}")
    
    if send_test_email(destino):
        print("\n" + "=" * 60)
        print("✅ ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("=" * 60)
        print("\n✨ El sistema está listo para enviar cotizaciones.")
    else:
        print("\n" + "=" * 60)
        print("❌ Error en el envío de correo")
        print("=" * 60)
