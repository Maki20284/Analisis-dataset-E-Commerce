import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bystate_df

def create_byscore_df(df):
    byscore_df = df.groupby(by="review_score").customer_id.nunique().reset_index()
    byscore_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return byscore_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

all_df = pd.read_csv("all_data.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
    
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    st.header("Rentang tanggal pemesanan dan waktu pengiriman")
    # Menambahkan logo
    st.image(
            "https://s3-us-west-2.amazonaws.com/uw-s3-cdn/wp-content/uploads/sites/6/2017/11/04133712/waterfall.jpg",
            width=200, # Manually Adjust the width of the image as per requirement
            )
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]
bystate_df = create_bystate_df(main_df)
byscore_df = create_byscore_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header(':sparkles: Proyek Analisis Data Pada E-Commerce')

st.subheader(":star: Demografis Pembeli")
 
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count", 
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Jumlah pembeli di negara bagian", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

with st.expander("Lihat penjelasan"):
    st.write(
        """
        Pada tabel tersebut terlihat persebaran demografis pembeli paling banyak berada di negara
        bagian SP yaitu sebanyak 40000 lebih.
        """
    )

st.subheader(":star: Kepuasan Pembeli")
 
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count", 
    y="review_score",
    data=byscore_df.sort_values(by="customer_count", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Tingkat kepuasan pembeli dalam berbelanja", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

with st.expander("Lihat penjelasan"):
    st.write(
        """
        Pada tabel tersebut terlihat bahwa tingkat kepuasan pembeli
        terhadap produk yang dijual sangat positif dengan menunjukkan rating 5 bintang.
        """
    )