import os
import time
import pandas as pd
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Apollo API Key (placeholder)
APOLLO_API_KEY = "J5BzL_W5Cg6iWbIWyglJWQ"

# CSV Paths
wheat_products_file = "asda_wheat_products.csv"
contact_list_file = "final_merged_contacts_cleaned.csv"

# Email Configuration
EMAIL_SENDER = "katiyar.sheelam1@gmail.com"
EMAIL_PASSWORD = "enpm ccmt lkpq wwrw"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Streamlit Configuration
st.set_page_config(page_title="AI Supplier Bot", layout="wide")
st.title("AI Supplier Bot: Connecting Suppliers & Buyers")

# Scrape ASDA Wheat-Based Products
st.header("🌾 Scrape ASDA Wheat-Based Products")

def scrape_asda():
    url = "https://groceries.asda.com/search/WHEAT"
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(5)

    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    products = driver.find_elements(By.CLASS_NAME, "co-product__anchor")
    prices = driver.find_elements(By.CLASS_NAME, "co-product__price")

    product_list = []
    for i in range(len(products)):
        try:
            name = products[i].text.strip()
            link = products[i].get_attribute("href")
            price = prices[i].text.strip() if i < len(prices) else "N/A"
            product_list.append({
                "Product Name": name,
                "Price": price,
                "Product Link": link
            })
        except Exception as e:
            print(f"Error extracting product {i}: {e}")

    driver.quit()

    os.makedirs(os.path.dirname(wheat_products_file), exist_ok=True)
    df = pd.DataFrame(product_list)
    df.to_csv(wheat_products_file, index=False)
    return df

if st.button("🔍 Start Scraping"):
    with st.spinner("Scraping ASDA for wheat-based products..."):
        df = scrape_asda()
        st.success("✅ Scraping Completed!")
        st.dataframe(df)

# Load Contact List
st.header("📋 Final Contact List")
if os.path.exists(contact_list_file):
    df_contacts = pd.read_csv(contact_list_file)
    st.dataframe(df_contacts)
else:
    st.warning("⚠️ No contact list found.")

# Send Email Function
def send_email(sender_email, sender_password, recipient_email, subject, message):
    try:
        validate_email(recipient_email)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        return f"✅ Email sent successfully to {recipient_email}"

    except EmailNotValidError:
        return f"⚠️ Invalid email address: {recipient_email}"
    except Exception as e:
        return f"❌ Failed to send email: {e}"

# Send Real Emails
st.subheader("📬 Send Emails to Buyers")

if st.button("📤 Send Emails to Buyers"):
    email_status = []
    for index, row in df_contacts.iterrows():
        name = row.get("Name", "Contact")
        job_title = row.get("Job Title", "Unknown")
        company = row.get("Company", "Unknown")
        recipient_email = row.get("Email", "").strip()

        if not recipient_email:
            email_status.append(f"⚠️ Missing email for {name} at {company}. Skipping.")
            continue

        try:
            validate_email(recipient_email)

            subject = f"Wheat Supply Partnership Opportunity – {company}"
            message = f"""
Dear {name},

We hope this message finds you well. 

I am Sheelam from **Organic Wheat Farm**, a trusted supplier of premium organic wheat products. We are exploring new collaborations with companies like **{company}** and identified you ({job_title}) as a key decision-maker.

We would love to discuss potential partnership opportunities and how we can support your wheat-based supply needs.

Looking forward to connecting with you.

Best Regards,  
**Sheelam**  
Organic Wheat Farm  
            """

            status = send_email(EMAIL_SENDER, EMAIL_PASSWORD, recipient_email, subject, message)
            email_status.append(status)

        except EmailNotValidError:
            email_status.append(f"⚠️ Invalid email address for {name} at {company}: {recipient_email}")
        except Exception as e:
            email_status.append(f"❌ Error sending to {recipient_email}: {e}")

    st.write("\n".join(email_status))
    st.success("✅ Email campaign completed!")
