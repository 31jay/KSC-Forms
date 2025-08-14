import smtplib
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import logging
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_email_template():
    """Load email template from file"""
    try:
        with open('mail_template.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error("Email template file not found")
        return None
    except Exception as e:
        logger.error(f"Error loading email template: {str(e)}")
        return None

def get_smtp_config():
    """Get SMTP configuration from Streamlit secrets"""
    try:
        smtp_config = {
            'server': st.secrets["email"]["SMTP_SERVER"],
            'port': int(st.secrets["email"]["SMTP_PORT"]),
            'username': st.secrets["email"]["SMTP_USERNAME"],
            'password': st.secrets["email"]["SMTP_PASSWORD"],
            'sender_name': st.secrets["email"]["SENDER_NAME"],
            'sender_email': st.secrets["email"]["SENDER_EMAIL"]
        }
        return smtp_config
    except KeyError as e:
        logger.error(f"Missing email configuration: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error getting SMTP configuration: {str(e)}")
        return None

def create_email_content(recipient_name, team_name, submission_type, team_details=None):
    """Create personalized email content"""
    template = load_email_template()
    if not template:
        return None
    
    # Get current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Replace placeholders in template
    content = template.replace("{RECIPIENT_NAME}", recipient_name)
    content = content.replace("{TEAM_NAME}", team_name)
    content = content.replace("{SUBMISSION_TYPE}", submission_type)
    content = content.replace("{TIMESTAMP}", current_time)
    
    # Add team-specific details if provided
    if team_details and submission_type == "Team":
        team_info = f"""
        Team Name: {team_details['team_name']}
        Team Members: {team_details['member_count']} members
        """
        content = content.replace("{TEAM_DETAILS}", team_info)
    else:
        content = content.replace("{TEAM_DETAILS}", "")
    
    return content

def send_confirmation_email(recipient_email, recipient_name, team_name, submission_type, team_details=None, retry_count=3):
    """Send confirmation email to the recipient with improved connection handling"""
    
    for attempt in range(retry_count):
        try:
            # Get SMTP configuration
            smtp_config = get_smtp_config()
            if not smtp_config:
                logger.error("Failed to get SMTP configuration")
                return False
            
            # Create email content
            email_content = create_email_content(recipient_name, team_name, submission_type, team_details)
            if not email_content:
                logger.error("Failed to create email content")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = formataddr((smtp_config['sender_name'], smtp_config['sender_email']))
            msg['To'] = recipient_email
            
            # Subject line based on submission type
            if submission_type == "Team":
                subject = f"Team Application Confirmed - {team_name} | Knowledge Sharing Circle"
            else:
                subject = f"Application Confirmed - {team_name} | Knowledge Sharing Circle"
            
            msg['Subject'] = subject
            
            # Attach email body
            msg.attach(MIMEText(email_content, 'plain', 'utf-8'))
            
            # Enhanced SMTP connection with better error handling
            server = None
            try:
                # Create SMTP connection
                server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
                server.set_debuglevel(0)  # Set to 1 for debugging
                
                # Enhanced connection setup
                server.ehlo()  # Identify ourselves to smtp gmail client
                server.starttls()  # Enable security
                server.ehlo()  # Re-identify ourselves as an encrypted connection
                
                # Login with credentials
                server.login(smtp_config['username'], smtp_config['password'])
                
                # Send email
                text = msg.as_string()
                server.sendmail(smtp_config['sender_email'], recipient_email, text)
                
                # Close connection properly
                server.quit()
                
                logger.info(f"Confirmation email sent successfully to {recipient_email}")
                return True
                
            except smtplib.SMTPServerDisconnected:
                logger.warning(f"SMTP Server disconnected on attempt {attempt + 1}")
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                
                # Wait before retry
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise
                    
            except Exception as e:
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                raise e
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {str(e)}")
            logger.error("Check your email credentials in secrets.toml")
            return False
            
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"Recipient email refused: {recipient_email} - {str(e)}")
            return False
            
        except smtplib.SMTPServerDisconnected as e:
            logger.error(f"SMTP Server disconnected after {retry_count} attempts: {str(e)}")
            return False
            
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP Connection error: {str(e)}")
            return False
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP Error: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error sending email to {recipient_email}: {str(e)}")
            return False
    
    return False

def test_email_connection():
    """Test email connection and configuration with enhanced diagnostics"""
    try:
        smtp_config = get_smtp_config()
        if not smtp_config:
            return False, "Failed to get SMTP configuration from secrets.toml"
        
        # Test connection step by step
        server = None
        try:
            # Step 1: Connect to server
            server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
            server.set_debuglevel(0)
            
            # Step 2: Start TLS
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            # Step 3: Login
            server.login(smtp_config['username'], smtp_config['password'])
            
            # Step 4: Close connection
            server.quit()
            
            return True, "Email connection successful - all steps completed"
            
        except smtplib.SMTPAuthenticationError as e:
            return False, f"Authentication failed: {str(e)}. Check username/password in secrets.toml"
        except smtplib.SMTPConnectError as e:
            return False, f"Connection failed: {str(e)}. Check SMTP server and port"
        except smtplib.SMTPServerDisconnected as e:
            return False, f"Server disconnected: {str(e)}. Try again or check network"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
        finally:
            if server:
                try:
                    server.quit()
                except:
                    pass
        
    except Exception as e:
        return False, f"Test failed: {str(e)}"

# Alternative email sending function for problematic SMTP servers
def send_email_alternative_method(recipient_email, recipient_name, team_name, submission_type, team_details=None):
    """Alternative email sending method using different SMTP approach"""
    try:
        smtp_config = get_smtp_config()
        if not smtp_config:
            return False
        
        email_content = create_email_content(recipient_name, team_name, submission_type, team_details)
        if not email_content:
            return False
        
        # Create simple message
        msg = MIMEText(email_content, 'plain', 'utf-8')
        msg['Subject'] = f"Application Confirmed - {team_name} | Knowledge Sharing Circle"
        msg['From'] = smtp_config['sender_email']
        msg['To'] = recipient_email
        
        # Use context manager for automatic cleanup
        with smtplib.SMTP_SSL(smtp_config['server'], 465) as server:  # Try SSL instead of TLS
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
        
        logger.info(f"Email sent via alternative method to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Alternative email method failed: {str(e)}")
        return False