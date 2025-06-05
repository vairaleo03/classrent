import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from ..config import settings

class EmailService:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.username = settings.email_username
        self.password = settings.email_password
    
    async def send_email(self, to_email: str, subject: str, body: str):
        """Invia email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.username, to_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Errore invio email: {e}")
            return False
    
    async def send_booking_confirmation(self, to_email: str, booking: dict, space: dict):
        """Invia conferma prenotazione"""
        subject = f"Conferma Prenotazione - {space['name']}"
        
        body = f"""
        <h2>Conferma Prenotazione ClassRent</h2>
        <p>La tua prenotazione è stata confermata con successo!</p>
        
        <h3>Dettagli Prenotazione:</h3>
        <ul>
            <li><strong>Spazio:</strong> {space['name']}</li>
            <li><strong>Luogo:</strong> {space['location']}</li>
            <li><strong>Data e Ora:</strong> {booking.start_datetime.strftime('%d/%m/%Y %H:%M')} - {booking.end_datetime.strftime('%H:%M')}</li>
            <li><strong>Scopo:</strong> {booking.purpose}</li>
            <li><strong>Materiali richiesti:</strong> {', '.join(booking.materials_requested) if booking.materials_requested else 'Nessuno'}</li>
        </ul>
        
        <p>Ti invieremo un promemoria 24 ore prima dell'appuntamento.</p>
        
        <p>Grazie per aver utilizzato ClassRent!</p>
        """
        
        await self.send_email(to_email, subject, body)
    
    async def send_reminder(self, to_email: str, booking_id: str):
        """Invia promemoria prenotazione"""
        # Recupera dettagli prenotazione dal DB
        subject = "Promemoria Prenotazione ClassRent"
        
        body = f"""
        <h2>Promemoria Prenotazione</h2>
        <p>Ti ricordiamo che domani hai una prenotazione su ClassRent.</p>
        <p>Controlla i dettagli nell'app per maggiori informazioni.</p>
        """
        
        await self.send_email(to_email, subject, body)

email_service = EmailService()