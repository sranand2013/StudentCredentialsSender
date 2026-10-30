import streamlit as st
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# --- CONFIGURATION MANAGEMENT ---
CONFIG_FILE = "config.json"

DEFAULT_TEMPLATE = """Hello,

Your student account has been successfully generated. Below are your login credentials:

Student Email: {email}
Password: {password}

Please ensure you change your password upon your first login.

Best Regards,
Organization Admin"""

def load_config():
    """Loads saved settings from a local JSON file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"org_email": "", "org_password": "", "sender_alias": "", "email_template": DEFAULT_TEMPLATE}

def save_config(email, password, alias, template):
    """Saves settings to a local JSON file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump({
            "org_email": email,
            "org_password": password,
            "sender_alias": alias,
            "email_template": template
        }, f)

# Load existing configuration
config = load_config()

# --- STREAMLIT UI ---
st.set_page_config(page_title="Student Email Dispatcher", page_icon="✉️", layout="centered")

st.title("✉️ Student Email Dispatcher")
st.markdown("Send customized credential emails to students dynamically.")

# --- SETTINGS SECTION ---
st.subheader("1. Organization Settings")
st.info("Update your credentials or template here and click **Save Configuration** to remember them for next time.")

col1, col2 = st.columns(2)
with col1:
    org_email = st.text_input("Organization Gmail ID", value=config.get("org_email", ""))
with col2:
    org_password = st.text_input("Email Password (App Password)", type="password", value=config.get("org_password", ""))

sender_alias = st.text_input(
    "Sender Name / Alias (Optional)", 
    value=config.get("sender_alias", ""), 
    placeholder="e.g., Student Admin"
)

email_template = st.text_area(
    "Customized Message Body (Use {email} and {password} to inject variables)", 
    value=config.get("email_template", DEFAULT_TEMPLATE), 
    height=250
)

if st.button("💾 Save Configuration", use_container_width=True):
    save_config(org_email, org_password, sender_alias, email_template)
    st.success("Settings saved! They will automatically load next time you open the app.")

st.divider()

# --- STUDENT DETAILS SECTION ---
st.subheader("2. Student Details (Recipient)")
col3, col4 = st.columns(2)
with col3:
    student_email = st.text_input("Student Email ID", placeholder="student@example.com")
with col4:
    student_password = st.text_input("Student Password", placeholder="Enter assigned password")

# --- SEND ACTION ---
if st.button("📤 Send Email", type="primary", use_container_width=True):
    if not all([org_email, org_password, student_email, student_password, email_template]):
        st.error("Please fill out all mandatory fields (Alias is optional) before sending.")
    else:
        try:
            with st.spinner(f"Sending email to {student_email}... Please check your terminal for debug logs."):
                # Inject variables into the template
                formatted_message = email_template.format(email=student_email, password=student_password)
                
                # Construct the email
                msg = MIMEMultipart()
                
                # Format the From header with a Display Name
                alias_name = sender_alias.strip() if sender_alias.strip() else "Organization Admin"
                msg['From'] = formataddr((alias_name, org_email))
                
                msg['To'] = student_email
                msg['Subject'] = "Your Student Account Credentials"
                msg.attach(MIMEText(formatted_message, 'plain'))
                
                # Connect to Gmail SMTP server and send using SSL (Port 465)
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                
                # ENABLE DEBUGGING - output goes to the terminal
                server.set_debuglevel(1) 
                
                server.login(org_email, org_password)
                server.send_message(msg)
                server.quit()
                
            st.success(f"✅ Email successfully sent to {student_email}!")
            
        except smtplib.SMTPAuthenticationError:
            st.error("Authentication failed. Please check your Organization Email and App Password.")
            st.info("Look at the terminal window for the exact server response.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.info("Check the command prompt/terminal where you ran Streamlit. The debug logs will show exactly where the connection dropped.")