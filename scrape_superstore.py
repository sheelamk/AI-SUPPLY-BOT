import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def scrape_superstore(store_name, search_query):
    """
    Scrapes product data from ASDA, Tesco, or Sainsbury based on store name and search term.

    Parameters:
        store_name (str): Name of the supermarket (ASDA, Tesco, Sainsbury)
        search_query (str): Product search term (e.g., wheat, rice)

    Returns:
        pd.DataFrame: DataFrame with product details.
    """
    # Setup headless Chrome
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
                try:
                    name = products[i].text.strip()
                    link = products[i].get_attribute("href")
                    price = prices[i].text.strip() if i < len(prices) else "N/A"
                    product_list.append({
                        "Store": "ASDA",
                        "Product Name": name,
                        "Price": price,
                        "Product Link": link
                    })
                except Exception as e:
                    print(f"Error at ASDA item {i}: {e}")

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
                try:
                    name = products[i].text.strip()
                    price = prices[i].text.strip() if i < len(prices) else "N/A"
                    product_list.append({
                        "Store": "Tesco",
                        "Product Name": name,
                        "Price": price,
                        "Product Link": "N/A"
                    })
                except Exception as e:
                    print(f"Error at Tesco item {i}: {e}")

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
                try:
                    name = products[i].text.strip()
                    price = prices[i].text.strip() if i < len(prices) else "N/A"
                    product_list.append({
                        "Store": "Sainsbury",
                        "Product Name": name,
                        "Price": price,
                        "Product Link": "N/A"
                    })
                except Exception as e:
                    print(f"Error at Sainsbury item {i}: {e}")

        else:
            print("❌ Store not supported. Choose from ASDA, Tesco, or Sainsbury.")

    except Exception as e:
        print(f"❌ Scraping failed for {store_name}: {e}")

    finally:
        driver.quit()

    return pd.DataFrame(product_list)
