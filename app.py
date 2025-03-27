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
st.title("🤖 AI Supplier Bot: Revolutionizing Supplier-Buyer Connections!")

st.markdown("""
Welcome to **AI Supplier Bot**! Your one-stop solution for automating supply chain connections!
This all-in-one tool empowers you to:
- Scrape products from top supermarkets
- Connect with verified supplier directories
- Reach out to potential buyers in one click
Let's revolutionize food supply chain sourcing together!
""")

# ---------- Product Scraper ----------
st.header("🌾 Scrape Supermarket Products")
with st.expander("🕽️ Click to expand scraping options"):
    st.markdown("Search for food products from ASDA, Tesco, or Sainsbury using keywords like 'wheat', 'rice', 'sugar', or 'pulses'.")
    store = st.selectbox("Choose Store:", ["ASDA", "Tesco", "Sainsbury"])
    search_term = st.text_input("Enter product search term:", "wheat")

    def scrape_superstore(store_name, search_query):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        options.add_argument(f"--user-data-dir=/tmp/chrome-user-data-{int(time.time())}")

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

        df = pd.DataFrame(product_list)
        filename = f"scraped_{store_name.lower()}_{search_query.lower().replace(' ', '_')}.csv"
        df.to_csv(filename, index=False)
        return df

    if st.button("🔍 Scrape Now"):
        with st.spinner("Scraping store..."):
            scraped_df = scrape_superstore(store, search_term)
            st.success("✅ Scraping Completed!")
            st.dataframe(scraped_df)

