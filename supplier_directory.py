import os
import pandas as pd
import streamlit as st

# Path to your supplier CSV file
supplier_file = "verified_suppliers.csv"

# 🌟 App Title
st.set_page_config(page_title="Supplier Directory", layout="wide")
st.title("📇 Verified Supplier Directory")

# Load and display supplier data
if os.path.exists(supplier_file):
    df_suppliers = pd.read_csv(supplier_file)

    # 🎯 Filters
    product_types = ["All"] + sorted(df_suppliers["Product Type"].dropna().unique())
    selected_type = st.selectbox("Filter by Product Type:", product_types)
    show_verified = st.checkbox("Show only verified suppliers", value=True)

    filtered_df = df_suppliers.copy()
    if selected_type != "All":
        filtered_df = filtered_df[filtered_df["Product Type"] == selected_type]
    if show_verified:
        filtered_df = filtered_df[filtered_df["Verified"].str.lower() == "yes"]

    st.dataframe(filtered_df)

    # ⬇️ Download filtered list
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Filtered Suppliers", data=csv, file_name="filtered_suppliers.csv", mime="text/csv")
else:
    st.warning("⚠️ `verified_suppliers.csv` not found. Please upload a file to get started.")

# 📤 Upload new suppliers
st.subheader("📤 Upload New Suppliers (CSV)")
uploaded_file = st.file_uploader("Upload a CSV with columns: Supplier Name, Product Type, Location, Email, Phone, Verified", type="csv")

if uploaded_file:
    try:
        new_df = pd.read_csv(uploaded_file)
        required_cols = {"Supplier Name", "Product Type", "Location", "Email", "Phone", "Verified"}

        if not required_cols.issubset(new_df.columns):
            st.error(f"❌ Uploaded CSV is missing required columns: {', '.join(required_cols)}")
        else:
            if os.path.exists(supplier_file):
                existing_df = pd.read_csv(supplier_file)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True).drop_duplicates()
            else:
                combined_df = new_df

            combined_df.to_csv(supplier_file, index=False)
            st.success("✅ Suppliers uploaded and saved successfully!")
            st.dataframe(combined_df)

    except Exception as e:
        st.error(f"❌ Failed to read CSV file: {e}")
