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

# ---------- Configuration ----------
APOLLO_API_KEY = "J5BzL_W5Cg6iWbIWyglJWQ"
EMAIL_SENDER = "katiyar.sheelam1@gmail.com"
EMAIL_PASSWORD = "enpm ccmt lkpq wwrw"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Files
CONTACTS_FILE = "final_merged_contacts_combined.csv"
SUPPLIER_FILE = "verified_suppliers.csv"

# ---------- UI Setup ----------
st.set_page_config(page_title="AI Supplier Bot", layout="wide")
st.title("🤖 AI Supplier Bot: : Revolutionizing Supplier-Buyer Connections! ")

st.markdown("""
Welcome to **AI Supplier Bot**! Your one-stop solution for automating supply chain connections! \n"
This all-in-one tool empowers you to:
- Scrape products from top supermarkets
- Connect with verified supplier directories
- Reach out to potential buyers in one click
Let's revolutionize food supply chain sourcing together!
""")

# ---------- Product Scraper ----------
st.header("🌾 Scrape Supermarket Products")
with st.expander("🔽 Click to expand scraping options"):
    st.markdown("Search for food products from ASDA, Tesco, or Sainsbury using keyword like 'wheat' or 'rice' or 'sugar' or 'pulses.")
    store = st.selectbox("Choose Store:", ["ASDA", "Tesco", "Sainsbury"])
    search_term = st.text_input("Enter product search term:", "wheat")

    def scrape_superstore(store_name, search_query):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        product_list = []

        try:
            if store_name.lower() == "asda":
                url = f"https://groceries.asda.com/search/{search_query}"
                driver.get(url)
                time.sleep(5)
                for _ in range(3):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                products = driver.find_elements(By.CLASS_NAME, "co-product__anchor")
                prices = driver.find_elements(By.CLASS_NAME, "co-product__price")
                for i in range(len(products)):
                    product_list.append({
                        "Store": "ASDA",
                        "Product Name": products[i].text.strip(),
                        "Price": prices[i].text.strip() if i < len(prices) else "N/A",
                        "Product Link": products[i].get_attribute("href")
                    })

            elif store_name.lower() == "tesco":
                url = f"https://www.tesco.com/groceries/en-GB/search?query={search_query}"
                driver.get(url)
                time.sleep(5)
                for _ in range(3):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                products = driver.find_elements(By.CLASS_NAME, "product-tile--title")
                prices = driver.find_elements(By.CLASS_NAME, "value")
                for i in range(len(products)):
                    product_list.append({
                        "Store": "Tesco",
                        "Product Name": products[i].text.strip(),
                        "Price": prices[i].text.strip() if i < len(prices) else "N/A",
                        "Product Link": "N/A"
                    })

            elif store_name.lower() == "sainsbury":
                url = f"https://www.sainsburys.co.uk/gol-ui/SearchResults/{search_query}"
                driver.get(url)
                time.sleep(5)
                for _ in range(3):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                products = driver.find_elements(By.CLASS_NAME, "productNameAndPromotions")
                prices = driver.find_elements(By.CLASS_NAME, "pricePerUnit")
                for i in range(len(products)):
                    product_list.append({
                        "Store": "Sainsbury",
                        "Product Name": products[i].text.strip(),
                        "Price": prices[i].text.strip() if i < len(prices) else "N/A",
                        "Product Link": "N/A"
                    })

        finally:
            driver.quit()

        return pd.DataFrame(product_list)

    if st.button("🔍 Scrape Now"):
        with st.spinner("Scraping store..."):
            scraped_df = scrape_superstore(store, search_term)
            st.success("✅ Scraping Completed!")
            st.dataframe(scraped_df)

# ---------- Buyer Contact List ----------
st.header("📇 Buyer Contact List")
with st.expander("🔽 View and manage buyer contacts"):
    if os.path.exists(CONTACTS_FILE):
        time.sleep(9)
        df_contacts = pd.read_csv(CONTACTS_FILE)
        st.markdown("These are the decision-makers you'll be reaching out to.")
        st.dataframe(df_contacts)
    else:
        st.error(f"❌ Contact file not found: {CONTACTS_FILE}")

# ---------- Send Emails ----------
st.header("📤 Email Buyers Instantly")
with st.expander("🔽 Expand to send email campaigns"):
    st.markdown("Craft personalized email campaigns with a single click. AI makes the outreach effortless!")

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
            return f"✅ Sent to {recipient_email}"

        except EmailNotValidError:
            return f"⚠️ Invalid email: {recipient_email}"
        except Exception as e:
            return f"❌ Failed: {e}"

    if st.button("📬 Send Emails to Buyers"):
        statuses = []
        for _, row in df_contacts.iterrows():
            name = row.get("Name", "Contact")
            job = row.get("Job Title", "Unknown")
            company = row.get("Company", "Unknown")
            email = row.get("Email", "").strip()

            if not email:
                statuses.append(f"⚠️ Missing email for {name} at {company}")
                continue

            subject = f"Wheat Supply Partnership – {company}"
            message = f"""
Dear {name},

We hope this message finds you well.

Dear {name},

I hope you're doing well. My name is Sheelam, and I represent Organic Wheat Farm, a trusted supplier of premium organic wheat. 
We believe that {company} could be an excellent partner for our high-quality products.
I would welcome the opportunity to discuss how we might work together to meet your supply needs.

Warm regards,
Sheelam
Organic Wheat Farm
            """
            statuses.append(send_email(EMAIL_SENDER, EMAIL_PASSWORD, email, subject, message))

        st.write("\n".join(statuses))
        st.success("✅ Email campaign finished.")

# ---------- Supplier Directory ----------
st.header("📦 Verified Supplier Directory")
with st.expander("🔽 Explore and manage suppliers"):
    st.markdown("Browse verified suppliers by product type, and even upload your own supplier list!")

    if os.path.exists(SUPPLIER_FILE):
        df_suppliers = pd.read_csv(SUPPLIER_FILE)
        types = ["All"] + sorted(df_suppliers["Product Type"].dropna().unique())
        selected_type = st.selectbox("Filter by Product Type:", types)
        show_verified = st.checkbox("Show only verified", value=True)

        filtered = df_suppliers.copy()
        if selected_type != "All":
            filtered = filtered[filtered["Product Type"] == selected_type]
        if show_verified:
            filtered = filtered[filtered["Verified"].str.lower() == "yes"]

        st.dataframe(filtered)
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Filtered Suppliers", data=csv, file_name="filtered_suppliers.csv", mime="text/csv")
    else:
        st.warning("⚠️ Supplier file not found.")

    st.markdown("---")
    st.subheader("📤 Upload New Suppliers")
    uploaded_file = st.file_uploader("Upload CSV (columns: Supplier Name, Product Type, Location, Email, Phone, Verified)", type="csv")
    if uploaded_file:
        new_df = pd.read_csv(uploaded_file)
        required_cols = {"Supplier Name", "Product Type", "Location", "Email", "Phone", "Verified"}

        if not required_cols.issubset(new_df.columns):
            st.error("❌ Missing required columns.")
        else:
            if os.path.exists(SUPPLIER_FILE):
                existing = pd.read_csv(SUPPLIER_FILE)
                combined = pd.concat([existing, new_df], ignore_index=True).drop_duplicates()
            else:
                combined = new_df

            combined.to_csv(SUPPLIER_FILE, index=False)
            st.success("✅ New suppliers added.")
            st.dataframe(combined)
