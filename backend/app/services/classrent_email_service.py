import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..config import settings
from ..database import get_database
from bson import ObjectId

class ClassRentEmailService:
    def __init__(self):
        # CONFIGURAZIONE FISSA PER CLASSRENT
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "classrent2025@gmail.com"
        self.sender_name = "ClassRent Sistema Universitario"
        
        # Password da settings per sicurezza
        self.sender_password = settings.email_password
        
        self.is_configured = self._check_configuration()
        
        if self.is_configured:
            print(f"✅ Servizio Email ClassRent configurato: {self.sender_email}")
        else:
            print("⚠️ Servizio Email ClassRent non configurato")
    
    def _check_configuration(self) -> bool:
        """Verifica se il servizio email è configurato correttamente"""
        return (
            self.sender_password is not None and
            len(self.sender_password) > 8  # App password minima
        )
    
    async def send_email(self, to_email: str, subject: str, body: str, cc_emails: List[str] = None) -> bool:
        """
        Invia email DA classrent2025@gmail.com A qualsiasi utente registrato
        """
        if not self.is_configured:
            print(f"📧 Email non configurata - skip invio a {to_email}")
            return False
            
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Reply-To'] = self.sender_email
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Corpo email HTML
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # Invio tramite SMTP Gmail
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            
            recipients = [to_email]
            if cc_emails:
                recipients.extend(cc_emails)
            
            server.sendmail(self.sender_email, recipients, msg.as_string())
            server.quit()
            
            print(f"✅ Email inviata DA {self.sender_email} A {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Errore invio email DA {self.sender_email} A {to_email}: {e}")
            return False
    
    async def send_booking_confirmation(self, user_email: str, booking: Dict, space: Dict, user_name: str = "Utente") -> bool:
        """
        Invia conferma prenotazione DA classrent2025@gmail.com AL utente che ha prenotato
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
            
            subject = f"✅ Conferma Prenotazione ClassRent - {space['name']}"
            
            # Template email professionale
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                    .header {{ background: linear-gradient(135deg, #1976d2, #42a5f5); color: white; padding: 40px 30px; text-align: center; }}
                    .logo {{ font-size: 28px; font-weight: bold; margin-bottom: 10px; }}
                    .content {{ padding: 40px 30px; }}
                    .footer {{ background: #f5f5f5; padding: 30px; text-align: center; font-size: 12px; color: #666; }}
                    .booking-card {{ background: #f8f9fa; border-left: 4px solid #1976d2; padding: 25px; margin: 25px 0; border-radius: 8px; }}
                    .info-row {{ display: flex; justify-content: space-between; margin: 12px 0; padding: 10px 0; border-bottom: 1px solid #eee; }}
                    .info-label {{ font-weight: bold; color: #555; }}
                    .info-value {{ color: #333; }}
                    .materials {{ background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .btn {{ display: inline-block; background: #1976d2; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 15px 10px; font-weight: bold; }}
                    .alert {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .success-badge {{ background: #4caf50; color: white; padding: 8px 16px; border-radius: 20px; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🎓 ClassRent</div>
                        <h1>Prenotazione Confermata!</h1>
                        <div class="success-badge">✅ Confermata Automaticamente</div>
                    </div>
                    
                    <div class="content">
                        <h2>Ciao {user_name}!</h2>
                        <p>La tua prenotazione è stata <strong>confermata automaticamente</strong> nel sistema ClassRent.</p>
                        
                        <div class="booking-card">
                            <h3>📋 Dettagli Prenotazione</h3>
                            <div class="info-row">
                                <span class="info-label">🏫 Spazio:</span>
                                <span class="info-value"><strong>{space['name']}</strong></span>
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
                                <span class="info-value">{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')} <small>({duration_hours:.1f} ore)</small></span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">🎯 Scopo:</span>
                                <span class="info-value">{booking['purpose']}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">👥 Capacità:</span>
                                <span class="info-value">{space.get('capacity', 'N/A')} persone</span>
                            </div>
                        </div>
                        
                        {f'''
                        <div class="materials">
                            <h3>🔧 Materiali Richiesti:</h3>
                            <ul style="margin: 10px 0; padding-left: 20px;">
                                {"".join([f"<li style='margin: 5px 0;'>{material}</li>" for material in booking.get('materials_requested', [])])}
                            </ul>
                        </div>
                        ''' if booking.get('materials_requested') else ''}
                        
                        {f'''
                        <div class="alert">
                            <strong>📝 Note Aggiuntive:</strong><br>
                            {booking.get('notes', '')}
                        </div>
                        ''' if booking.get('notes') else ''}
                        
                        <div class="alert">
                            <strong>⏰ Promemoria Automatico:</strong><br>
                            Riceverai un reminder via email 24 ore prima dell'appuntamento.
                        </div>
                        
                        <h3>📝 Prossimi Passi:</h3>
                        <ul style="line-height: 1.8;">
                            <li>✅ <strong>Salva questa email</strong> come conferma ufficiale</li>
                            <li>📅 <strong>Segna il calendario</strong> - l'evento è stato aggiunto automaticamente</li>
                            <li>🔧 <strong>Prepara i materiali</strong> richiesti per la sessione</li>
                            <li>⏰ <strong>Arriva 10 minuti prima</strong> per setup e preparazione</li>
                            <li>🆔 <strong>Porta documento</strong> o badge universitario per accesso</li>
                            <li>📞 <strong>Contatta supporto</strong> in caso di problemi urgenti</li>
                        </ul>
                        
                        <div style="text-align: center; margin: 40px 0;">
                            <a href="http://localhost:3000/bookings" class="btn">📋 Gestisci Prenotazioni</a>
                            <a href="http://localhost:3000/calendar" class="btn">📅 Vedi Calendario</a>
                        </div>
                        
                        <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; text-align: center;">
                            <h4>🤖 Hai usato l'AI Assistant?</h4>
                            <p>Puoi sempre chiedere aiuto al nostro assistente AI per future prenotazioni!</p>
                            <a href="http://localhost:3000/chat" class="btn" style="background: #4caf50;">💬 Apri Chat AI</a>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p><strong>ClassRent</strong> - Sistema di Prenotazione Aule Universitarie</p>
                        <p>📧 Email automatica generata il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}</p>
                        <p>🆘 Supporto: <a href="mailto:{self.sender_email}">classrent2025@gmail.com</a> | 📞 +39 XXX XXX XXXX</p>
                        <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                        <p style="font-size: 10px;">
                            Questa email è stata inviata perché hai effettuato una prenotazione su ClassRent.<br>
                            Università di [Nome] - Servizi Digitali per Studenti
                        </p>
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
        """Invia reminder 24h prima della prenotazione"""
        if not self.is_configured:
            return False
        
        try:
            # Recupera dettagli prenotazione
            db = await get_database()
            booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
            if not booking:
                return False
            
            space = await db.spaces.find_one({"_id": ObjectId(booking["space_id"])})
            user = await db.users.find_one({"_id": ObjectId(booking["user_id"])})
            
            if not space or not user:
                return False
            
            start_dt = booking['start_datetime']
            subject = f"⏰ Reminder ClassRent: Prenotazione domani - {space['name']}"
            
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                    .header {{ background: linear-gradient(135deg, #ff9800, #ffb74d); color: white; padding: 40px 30px; text-align: center; }}
                    .content {{ padding: 40px 30px; }}
                    .footer {{ background: #f5f5f5; padding: 30px; text-align: center; font-size: 12px; color: #666; }}
                    .reminder-card {{ background: #fff3e0; border-left: 4px solid #ff9800; padding: 25px; margin: 25px 0; border-radius: 8px; }}
                    .checklist {{ background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .btn {{ display: inline-block; background: #ff9800; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 10px 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div style="font-size: 24px; font-weight: bold;">🎓 ClassRent</div>
                        <h1>⏰ Reminder Prenotazione</h1>
                        <p>La tua prenotazione è <strong>domani</strong>!</p>
                    </div>
                    
                    <div class="content">
                        <h2>Ciao {user['full_name']}!</h2>
                        
                        <div class="reminder-card">
                            <h3>📋 Riepilogo Prenotazione</h3>
                            <p><strong>🏫 Spazio:</strong> {space['name']}</p>
                            <p><strong>📍 Dove:</strong> {space['location']}</p>
                            <p><strong>🕐 Quando:</strong> Domani, {start_dt.strftime('%H:%M')} - {booking['end_datetime'].strftime('%H:%M')}</p>
                            <p><strong>🎯 Scopo:</strong> {booking['purpose']}</p>
                        </div>
                        
                        <div class="checklist">
                            <h3>✅ Checklist Pre-Appuntamento:</h3>
                            <ul style="line-height: 1.8;">
                                <li>🎒 Preparare tutti i materiali necessari</li>
                                <li>🔧 Verificare attrezzature: {', '.join(booking.get('materials_requested', ['Nessuno']))}</li>
                                <li>⏰ <strong>Arrivare 10 minuti prima</strong> dell'orario</li>
                                <li>🔑 Portare badge/tessera universitaria</li>
                                <li>📱 Avere contatti di emergenza</li>
                                <li>💻 Testare presentazioni (se applicabile)</li>
                            </ul>
                        </div>
                        
                        <div style="background: #ffebee; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <strong>🚨 Importante:</strong><br>
                            Se non puoi più partecipare, <strong>cancella la prenotazione</strong> per permettere ad altri di utilizzare lo spazio.
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="http://localhost:3000/bookings" class="btn">📋 Gestisci Prenotazione</a>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p><strong>ClassRent</strong> - Reminder automatico</p>
                        <p>Ricevi questo reminder perché la tua prenotazione è tra 24 ore</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return await self.send_email(user_email, subject, body)
            
        except Exception as e:
            print(f"❌ Errore invio reminder: {e}")
            return False
    
    async def send_booking_cancellation(self, user_email: str, booking: Dict, space: Dict, user_name: str = "Utente", reason: str = "") -> bool:
        """Invia notifica cancellazione"""
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
                    .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                    .header {{ background: linear-gradient(135deg, #f44336, #ef5350); color: white; padding: 40px 30px; text-align: center; }}
                    .content {{ padding: 40px 30px; }}
                    .footer {{ background: #f5f5f5; padding: 30px; text-align: center; font-size: 12px; color: #666; }}
                    .cancellation-card {{ background: #ffebee; border-left: 4px solid #f44336; padding: 25px; margin: 25px 0; border-radius: 8px; }}
                    .btn {{ display: inline-block; background: #1976d2; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 10px 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div style="font-size: 24px; font-weight: bold;">🎓 ClassRent</div>
                        <h1>❌ Prenotazione Cancellata</h1>
                    </div>
                    
                    <div class="content">
                        <h2>Ciao {user_name},</h2>
                        <p>La tua prenotazione è stata <strong>cancellata</strong> dal sistema ClassRent.</p>
                        
                        <div class="cancellation-card">
                            <h3>Dettagli Prenotazione Cancellata:</h3>
                            <p><strong>🏫 Spazio:</strong> {space['name']}</p>
                            <p><strong>📍 Ubicazione:</strong> {space['location']}</p>
                            <p><strong>📅 Data:</strong> {start_dt.strftime('%d/%m/%Y alle %H:%M')}</p>
                            <p><strong>🎯 Scopo:</strong> {booking['purpose']}</p>
                            {f"<p><strong>📝 Motivo:</strong> {reason}</p>" if reason else ""}
                        </div>
                        
                        <p>✅ Lo spazio è ora <strong>nuovamente disponibile</strong> per altre prenotazioni.</p>
                        
                        <div style="text-align: center; margin: 40px 0;">
                            <a href="http://localhost:3000/spaces" class="btn">🔍 Trova Altro Spazio</a>
                            <a href="http://localhost:3000/chat" class="btn">🤖 Chiedi all'AI Assistant</a>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p><strong>ClassRent</strong> - Notifica automatica</p>
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
    
    async def send_welcome_email(self, user_email: str, user_name: str, temp_password: str = None) -> bool:
        """Invia email di benvenuto ai nuovi utenti registrati"""
        if not self.is_configured:
            return False
        
        try:
            subject = f"🎓 Benvenuto su ClassRent - {user_name}!"
            
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                    .header {{ background: linear-gradient(135deg, #4caf50, #66bb6a); color: white; padding: 40px 30px; text-align: center; }}
                    .content {{ padding: 40px 30px; }}
                    .footer {{ background: #f5f5f5; padding: 30px; text-align: center; font-size: 12px; color: #666; }}
                    .welcome-card {{ background: #e8f5e8; border-left: 4px solid #4caf50; padding: 25px; margin: 25px 0; border-radius: 8px; }}
                    .btn {{ display: inline-block; background: #4caf50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 10px 5px; }}
                    .features {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div style="font-size: 28px; font-weight: bold;">🎓 ClassRent</div>
                        <h1>Benvenuto/a!</h1>
                        <p>Il tuo account è stato creato con successo</p>
                    </div>
                    
                    <div class="content">
                        <h2>Ciao {user_name}! 👋</h2>
                        
                        <div class="welcome-card">
                            <h3>🎉 Registrazione Completata!</h3>
                            <p>Il tuo account ClassRent è ora <strong>attivo</strong> e pronto all'uso.</p>
                            <p><strong>📧 Email:</strong> {user_email}</p>
                            {f"<p><strong>🔑 Password temporanea:</strong> {temp_password}</p>" if temp_password else ""}
                        </div>
                        
                        <div class="features">
                            <h3>🚀 Cosa puoi fare con ClassRent:</h3>
                            <ul style="line-height: 1.8;">
                                <li>📅 <strong>Prenotare aule e laboratori</strong> universitari</li>
                                <li>🤖 <strong>Usare l'AI Assistant</strong> per prenotazioni vocali</li>
                                <li>📊 <strong>Visualizzare calendario</strong> condiviso degli spazi</li>
                                <li>📧 <strong>Ricevere notifiche</strong> automatiche e reminder</li>
                                <li>🔧 <strong>Richiedere materiali</strong> specifici per le tue sessioni</li>
                                <li>📱 <strong>Gestire tutto dal mobile</strong> - responsive design</li>
                            </ul>
                        </div>
                        
                        <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h4>🤖 Prova l'AI Assistant!</h4>
                            <p>Dì semplicemente: <em>"Voglio prenotare un'aula per domani alle 14"</em></p>
                            <p>L'AI capirà la tua richiesta e ti aiuterà a trovare lo spazio perfetto!</p>
                        </div>
                        
                        <div style="text-align: center; margin: 40px 0;">
                            <a href="http://localhost:3000/dashboard" class="btn">🏠 Vai alla Dashboard</a>
                            <a href="http://localhost:3000/chat" class="btn" style="background: #1976d2;">💬 Prova AI Assistant</a>
                        </div>
                        
                        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h4>📋 Primi Passi Consigliati:</h4>
                            <ol style="line-height: 1.8;">
                                <li>Esplora gli <strong>spazi disponibili</strong> nel catalogo</li>
                                <li>Fai una <strong>prenotazione di prova</strong> per familiarizzare</li>
                                <li>Prova l'<strong>AI Assistant</strong> per prenotazioni veloci</li>
                                <li>Controlla la tua <strong>email regolarmente</strong> per notifiche</li>
                            </ol>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p><strong>ClassRent</strong> - Sistema di Prenotazione Aule Universitarie</p>
                        <p>🆘 Hai bisogno di aiuto? Scrivi a: <a href="mailto:{self.sender_email}">classrent2025@gmail.com</a></p>
                        <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                        <p style="font-size: 10px;">
                            Email di benvenuto automatica - {datetime.now().strftime('%d/%m/%Y alle %H:%M')}<br>
                            Università di [Nome] - Servizi Digitali per Studenti
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return await self.send_email(user_email, subject, body)
            
        except Exception as e:
            print(f"❌ Errore invio email benvenuto: {e}")
            return False

# Istanza globale del servizio
classrent_email_service = ClassRentEmailService()