import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..config import settings
from ..database import get_database
from bson import ObjectId

class EnhancedEmailService:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.username = settings.email_username
        self.password = settings.email_password
        self.is_configured = self._check_configuration()
        
        if self.is_configured:
            print("✅ Servizio Email configurato e pronto")
        else:
            print("⚠️ Servizio Email non configurato - le notifiche email saranno disabilitate")
    
    def _check_configuration(self) -> bool:
        """Verifica se il servizio email è configurato correttamente"""
        return (
            self.username is not None and
            self.password is not None and
            self.smtp_server is not None and
            self.smtp_port is not None and
            len(self.password) > 8  # App password minima
        )
    
    async def send_email(self, to_email: str, subject: str, body: str, cc_emails: List[str] = None) -> bool:
        """Invia email con supporto per CC"""
        if not self.is_configured:
            print(f"📧 Email non configurata - skip invio a {to_email}")
            return False
            
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"ClassRent System <{self.username}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Corpo email HTML
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # Invio
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            
            recipients = [to_email]
            if cc_emails:
                recipients.extend(cc_emails)
            
            server.sendmail(self.username, recipients, msg.as_string())
            server.quit()
            
            print(f"✅ Email inviata con successo a {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Errore invio email a {to_email}: {e}")
            return False
    
    async def send_booking_confirmation(self, user_email: str, booking: Dict, space: Dict) -> bool:
        """
        Invia email di conferma prenotazione PERSONALIZZATA per ogni utente
        """
        if not self.is_configured:
            return False
        
        try:
            # Calcola durata
            start_dt = booking['start_datetime']
            end_dt = booking['end_datetime']
            if isinstance(start_dt, str):
                start_dt = datetime.fromisoformat(start_dt.replace('Z', '+00:00'))
            if isinstance(end_dt, str):
                end_dt = datetime.fromisoformat(end_dt.replace('Z', '+00:00'))
            
            duration = end_dt - start_dt
            duration_hours = duration.total_seconds() / 3600
            
            subject = f"✅ Prenotazione Confermata - {space['name']}"
            
            # Template email personalizzato
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #1976d2, #42a5f5); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; }}
                    .footer {{ background: #f5f5f5; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #666; }}
                    .booking-card {{ background: #f8f9fa; border-left: 4px solid #1976d2; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .info-row {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 8px 0; border-bottom: 1px solid #eee; }}
                    .info-label {{ font-weight: bold; color: #555; }}
                    .info-value {{ color: #333; }}
                    .materials {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .btn {{ display: inline-block; background: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 5px; }}
                    .alert {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Prenotazione Confermata!</h1>
                        <p>La tua prenotazione è stata registrata con successo</p>
                    </div>
                    
                    <div class="content">
                        <h2>Dettagli della Prenotazione</h2>
                        
                        <div class="booking-card">
                            <div class="info-row">
                                <span class="info-label">🏫 Spazio:</span>
                                <span class="info-value">{space['name']}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">📍 Ubicazione:</span>
                                <span class="info-value">{space['location']}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">📅 Data:</span>
                                <span class="info-value">{start_dt.strftime('%A, %d %B %Y')}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">🕐 Orario:</span>
                                <span class="info-value">{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')} ({duration_hours:.1f}h)</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">🎯 Scopo:</span>
                                <span class="info-value">{booking['purpose']}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">👥 Capacità spazio:</span>
                                <span class="info-value">{space.get('capacity', 'N/A')} persone</span>
                            </div>
                        </div>
                        
                        {f'''
                        <div class="materials">
                            <h3>🔧 Materiali Richiesti:</h3>
                            <ul>
                                {"".join([f"<li>{material}</li>" for material in booking.get('materials_requested', [])])}
                            </ul>
                        </div>
                        ''' if booking.get('materials_requested') else ''}
                        
                        {f'''
                        <div class="alert">
                            <strong>📝 Note:</strong> {booking.get('notes', '')}
                        </div>
                        ''' if booking.get('notes') else ''}
                        
                        <div class="alert">
                            <strong>⏰ Reminder:</strong> Riceverai un promemoria automatico 24 ore prima dell'appuntamento.
                        </div>
                        
                        <h3>📋 Cosa fare ora:</h3>
                        <ul>
                            <li>✅ Salva questa email per riferimento</li>
                            <li>📅 L'evento è stato aggiunto al calendario (se configurato)</li>
                            <li>🔧 Verifica che i materiali richiesti siano disponibili</li>
                            <li>⏰ Arriva 10 minuti prima per il setup</li>
                            <li>🎓 In caso di problemi, contatta il supporto tecnico</li>
                        </ul>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://localhost:3000/bookings" class="btn">📋 Gestisci Prenotazioni</a>
                            <a href="http://localhost:3000/spaces" class="btn">🏫 Vedi Altri Spazi</a>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p><strong>ClassRent</strong> - Sistema di Prenotazione Aule Universitarie</p>
                        <p>Email generata automaticamente il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}</p>
                        <p>Per supporto: <a href="mailto:{self.username}">assistenza@classrent.edu</a></p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return await self.send_email(user_email, subject, body)
            
        except Exception as e:
            print(f"❌ Errore invio conferma prenotazione: {e}")
            return False
    
    async def send_booking_reminder(self, user_email: str, booking_id: str) -> bool:
        """
        Invia reminder 24h prima della prenotazione
        """
        if not self.is_configured:
            return False
        
        try:
            # Recupera dettagli prenotazione dal database
            db = await get_database()
            booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
            if not booking:
                print(f"⚠️ Prenotazione {booking_id} non trovata per reminder")
                return False
            
            space = await db.spaces.find_one({"_id": ObjectId(booking["space_id"])})
            user = await db.users.find_one({"_id": ObjectId(booking["user_id"])})
            
            if not space or not user:
                print(f"⚠️ Dati mancanti per reminder {booking_id}")
                return False
            
            start_dt = booking['start_datetime']
            end_dt = booking['end_datetime']
            
            subject = f"⏰ Reminder: Prenotazione domani - {space['name']}"
            
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #ff9800, #ffb74d); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; }}
                    .footer {{ background: #f5f5f5; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #666; }}
                    .reminder-card {{ background: #fff3e0; border-left: 4px solid #ff9800; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .info-row {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 8px 0; border-bottom: 1px solid #eee; }}
                    .info-label {{ font-weight: bold; color: #555; }}
                    .info-value {{ color: #333; }}
                    .checklist {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .btn {{ display: inline-block; background: #ff9800; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>⏰ Reminder Prenotazione</h1>
                        <p>La tua prenotazione è domani!</p>
                    </div>
                    
                    <div class="content">
                        <div class="reminder-card">
                            <h2>📋 Riepilogo Prenotazione</h2>
                            <div class="info-row">
                                <span class="info-label">🏫 Spazio:</span>
                                <span class="info-value">{space['name']}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">📍 Dove:</span>
                                <span class="info-value">{space['location']}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">🕐 Quando:</span>
                                <span class="info-value">Domani, {start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">🎯 Scopo:</span>
                                <span class="info-value">{booking['purpose']}</span>
                            </div>
                        </div>
                        
                        <div class="checklist">
                            <h3>✅ Checklist Pre-Appuntamento:</h3>
                            <ul>
                                <li>🎒 Preparare materiali necessari</li>
                                <li>🔧 Verificare disponibilità attrezzature: {', '.join(booking.get('materials_requested', ['Nessuno']))}</li>
                                <li>⏰ Arrivare 10 minuti prima</li>
                                <li>🔑 Portare badge/tessera di accesso</li>
                                <li>📱 Avere contatti di emergenza</li>
                                <li>💻 Testare presentazioni/file (se necessario)</li>
                            </ul>
                        </div>
                        
                        <div style="background: #ffebee; padding: 15px; border-radius: 5px; margin: 15px 0;">
                            <strong>🚨 Importante:</strong> Se non puoi più partecipare, cancella la prenotazione per permettere ad altri di utilizzare lo spazio.
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://localhost:3000/bookings" class="btn">📋 Gestisci Prenotazione</a>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p><strong>ClassRent</strong> - Reminder automatico</p>
                        <p>Hai ricevuto questo reminder perché la tua prenotazione è tra 24 ore</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return await self.send_email(user_email, subject, body)
            
        except Exception as e:
            print(f"❌ Errore invio reminder: {e}")
            return False
    
    async def send_booking_cancellation(self, user_email: str, booking: Dict, space: Dict, reason: str = "") -> bool:
        """
        Invia notifica di cancellazione prenotazione
        """
        if not self.is_configured:
            return False
        
        try:
            start_dt = booking['start_datetime']
            if isinstance(start_dt, str):
                start_dt = datetime.fromisoformat(start_dt.replace('Z', '+00:00'))
            
            subject = f"❌ Prenotazione Cancellata - {space['name']}"
            
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #f44336, #ef5350); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; }}
                    .footer {{ background: #f5f5f5; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #666; }}
                    .cancellation-card {{ background: #ffebee; border-left: 4px solid #f44336; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .btn {{ display: inline-block; background: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>❌ Prenotazione Cancellata</h1>
                        <p>La tua prenotazione è stata cancellata</p>
                    </div>
                    
                    <div class="content">
                        <div class="cancellation-card">
                            <h3>Dettagli Prenotazione Cancellata:</h3>
                            <p><strong>Spazio:</strong> {space['name']}</p>
                            <p><strong>Data:</strong> {start_dt.strftime('%d/%m/%Y alle %H:%M')}</p>
                            <p><strong>Scopo:</strong> {booking['purpose']}</p>
                            {f"<p><strong>Motivo cancellazione:</strong> {reason}</p>" if reason else ""}
                        </div>
                        
                        <p>Lo spazio è ora nuovamente disponibile per altre prenotazioni.</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://localhost:3000/spaces" class="btn">🔍 Trova Altro Spazio</a>
                            <a href="http://localhost:3000/bookings" class="btn">📋 Altre Prenotazioni</a>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p><strong>ClassRent</strong> - Notifica di cancellazione</p>
                        <p>Cancellazione processata il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return await self.send_email(user_email, subject, body)
            
        except Exception as e:
            print(f"❌ Errore invio cancellazione: {e}")
            return False
    
    async def send_bulk_notification(self, user_emails: List[str], subject: str, message: str, notification_type: str = "info") -> Dict[str, Any]:
        """
        Invia notifiche in massa (es. manutenzioni, chiusure, etc.)
        """
        if not self.is_configured:
            return {"sent": 0, "failed": len(user_emails), "errors": ["Email service not configured"]}
        
        sent_count = 0
        failed_count = 0
        errors = []
        
        # Template per notifiche di sistema
        colors = {
            "info": "#2196f3",
            "warning": "#ff9800", 
            "error": "#f44336",
            "success": "#4caf50"
        }
        
        color = colors.get(notification_type, "#2196f3")
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {color}; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; }}
                .footer {{ background: #f5f5f5; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📢 Notifica ClassRent</h1>
                </div>
                <div class="content">
                    {message}
                </div>
                <div class="footer">
                    <p><strong>ClassRent</strong> - Sistema di Prenotazione Aule</p>
                    <p>Notifica inviata il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        for email in user_emails:
            try:
                success = await self.send_email(email, subject, body)
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                    errors.append(f"Failed to send to {email}")
            except Exception as e:
                failed_count += 1
                errors.append(f"Error sending to {email}: {str(e)}")
        
        return {
            "sent": sent_count,
            "failed": failed_count,
            "total": len(user_emails),
            "errors": errors
        }

# Istanza globale del servizio
enhanced_email_service = EnhancedEmailService()