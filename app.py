import os
import time
import pandas as pd
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError

# ---------- Configuration ----------
EMAIL_SENDER = "katiyar.sheelam1@gmail.com"
EMAIL_PASSWORD = "enpm ccmt lkpq wwrw"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Files
CONTACTS_FILE = "final_merged_contacts_combined.csv"
SUPPLIER_FILE = "verified_suppliers.csv"
SCRAPED_FILES = [
    "asda_wheat.csv", "asda_rice.csv", "asda_sugar.csv", "asda_pulses.csv"
]

# ---------- UI Setup ----------
st.set_page_config(page_title="AI Supplier Bot 🤖", layout="wide")
st.title("🤖 AI Supplier Bot: Revolutionizing Supplier-Buyer Connections")

st.write(
    """
Welcome to **AI Supplier Bot**, your one-stop solution for automating supply chain connections!  We leverage AI and web scraping to bring **high-quality wheat products** and **verified buyers** together effortlessly.  
Say goodbye to **manual searching** and hello to **seamless AI-powered networking**.  Start **scraping ASDA wheat products**, **fetching buyers**, and **sending emails** – all in just a few clicks!
"""
)

# 📌 Step 1: Scrape ASDA Products
st.header("🌾 Scrape ASDA Products")
st.write("Instantly gather product details from ASDA to find new insights. Click below to begin!")

category = st.selectbox("Select product category:", ["wheat", "rice", "sugar", "pulses"])
if st.button("Search Products"):
    with st.spinner("Fetching product from ASDA..."):
        time.sleep(10)
        selected_files = [file for file in SCRAPED_FILES if category in file]
        all_data = []
        for file in selected_files:
            if os.path.exists(file) and os.path.getsize(file) > 0:
                df = pd.read_csv(file)
                df["Source File"] = file
                all_data.append(df)
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            st.success("Data fetched successfully")
            st.dataframe(combined_df)
            csv = combined_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, f"asda_{category}_products.csv", mime="text/csv")
        else:
            st.warning("No data found for the selected category.")

# 📇 Buyer Contact List
st.header("📇 Buyer Contact List")
st.write("Find decision-makers in supply chain and procurement. Click below to fetch real contacts!")
if os.path.exists(CONTACTS_FILE):
    if st.button("Show Buyers"):
        with st.spinner("Loading verified buyer contacts..."):
            time.sleep(10)
            df_contacts = pd.read_csv(CONTACTS_FILE)
            df_contacts = df_contacts[~df_contacts["Company"].str.lower().str.contains("tesco|sainsbury")]
            st.success("Buyers loaded successfully")
            st.dataframe(df_contacts)
else:
    st.error(f"❌ Contact file not found: {CONTACTS_FILE}")

# 📨 Email Buyers
st.header("📨 Email Buyers")
st.write("Instantly send outreach emails to potential buyers. Let’s get started!")
with st.expander("Send Email Campaign"):

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

    if st.button("Send Emails"):
        with st.spinner("Sending emails to buyers..."):
            time.sleep(10)
            if os.path.exists(CONTACTS_FILE):
                df_contacts = pd.read_csv(CONTACTS_FILE)
                df_contacts = df_contacts[~df_contacts["Company"].str.lower().str.contains("tesco|sainsbury")]
                statuses = []
                for _, row in df_contacts.iterrows():
                    name = row.get("Name", "Contact")
                    job = row.get("Job Title", "Unknown")
                    company = row.get("Company", "Unknown")
                    email = row.get("Email", "").strip()
                    if not email:
                        statuses.append(f"⚠️ Missing email for {name} at {company}")
                        continue
                    subject = f"Partnership Inquiry – {company}"
                    message = f"""
Dear {name},

I hope you're doing well. I'm Sheelam from Organic Wheat Farm, a trusted supplier of premium organic wheat, rice , sugar and pulses.  
We believe that {company} could be an excellent partner for our high-quality products.  
I'd be delighted to explore opportunities to work together.

Warm regards,  
Sheelam  
Organic Wheat Farm
                    """
                    statuses.append(send_email(EMAIL_SENDER, EMAIL_PASSWORD, email, subject, message))
                st.success("✅ Email campaign finished.")
                st.write("\n".join(statuses))
            else:
                st.error("❌ Contact file not found.")

# 📘 Supplier Directory
st.header("📘 Verified Supplier Directory")
st.write("Easily manage a list of trusted suppliers. Filter by type, verify, or upload more.")
with st.expander("View or Add Suppliers"):
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
        st.download_button("Download Supplier List", csv, "filtered_suppliers.csv", mime="text/csv")
    else:
        st.warning("Supplier file not found.")

    uploaded_file = st.file_uploader("Upload new supplier CSV (columns: Supplier Name, Product Type, Location, Email, Phone, Verified)", type="csv")
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
            st.success("✅ Suppliers updated.")
            st.dataframe(combined)

# Footer
st.markdown("---")
st.markdown("Created by Sheelam with dedication to making supply chains smarter and faster.")
