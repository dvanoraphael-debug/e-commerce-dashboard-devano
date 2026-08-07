import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Konfigurasi Halaman Dashboard
st.set_page_config(page_title="Dashboard Analisis Data E-Commerce", layout="wide")

# Function untuk Membaca Data
@st.cache_data
def load_data():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    path_same_dir = os.path.join(dir_path, 'main_data.csv')
    path_sub_dir = os.path.join(dir_path, 'dashboard', 'main_data.csv')
    
    if os.path.exists(path_same_dir):
        file_path = path_same_dir
    elif os.path.exists(path_sub_dir):
        file_path = path_sub_dir
    else:
        file_path = 'main_data.csv' if os.path.exists('main_data.csv') else 'dashboard/main_data.csv'
    
    df = pd.read_csv(file_path)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

df = load_data()

# Header Dashboard
st.title("Proyek Analisis Data: E-Commerce Dataset")
st.write("**Nama:** Devano Raphael Poli")
st.write("**Email:** dvanoraphael@gmail.com")

st.divider()

# Sidebar Filter Tanggal
st.sidebar.header("Filter Data")

min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()

start_date, end_date = st.sidebar.date_input(
    label='Rentang Waktu',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# Saring data berdasarkan tanggal pilihan
filtered_df = df[
    (df['order_purchase_timestamp'].dt.date >= start_date) & 
    (df['order_purchase_timestamp'].dt.date <= end_date)
]

# Metrik Utama (KPI)
col1, col2, col3 = st.columns(3)

total_orders = filtered_df['order_id'].nunique()
total_customers = filtered_df['customer_unique_id'].nunique()
delivered_orders = (filtered_df['order_status'] == 'delivered').sum()

col1.metric("Total Orders", f"{total_orders:,}")
col2.metric("Total Customers", f"{total_customers:,}")
col3.metric("Orders Delivered", f"{delivered_orders:,}")

st.divider()

# Pertanyaan 1: Performa Penjualan Kategori Produk
st.subheader("Pertanyaan 1: Apa saja kategori produk dengan performa penjualan terbaik dan terburuk?")

category_sales = filtered_df.groupby('product_category_name_english')['price'].sum().reset_index()

top_5 = category_sales.sort_values(by='price', ascending=False).head(5)
bottom_5 = category_sales.sort_values(by='price', ascending=True).head(5)

fig, ax = plt.subplots(1, 2, figsize=(12, 5))

# Plot Top 5
sns.barplot(data=top_5, x='price', y='product_category_name_english', ax=ax[0], color='skyblue')
ax[0].set_title("5 Kategori Produk Teratas (Pendapatan)")
ax[0].set_xlabel("Total Pendapatan ($)")
ax[0].set_ylabel("")

# Plot Bottom 5
sns.barplot(data=bottom_5, x='price', y='product_category_name_english', ax=ax[1], color='salmon')
ax[1].set_title("5 Kategori Produk Terbawah (Pendapatan)")
ax[1].set_xlabel("Total Pendapatan ($)")
ax[1].set_ylabel("")

plt.tight_layout()
st.pyplot(fig)

# Insight Pertanyaan 1
st.write("**Insight:**")
st.write("- Dominasi kategori *health_beauty* dan *watches_gifts* masing-masing berhasil menembus total pendapatan lebih dari $1,2 juta.")
st.write("- Kategori *security_and_services* berada di posisi paling dasar dengan total pendapatan terkecil, yaitu hanya $283,29.")
st.write("- Produk kebutuhan harian, gaya hidup, serta perlengkapan rumah tangga menjadi favorit utama pelanggan, sementara produk hobi dengan pasar terbatas berada di urutan paling bawah.")

st.divider()

# Pertanyaan 2: Tren Pesanan Bulanan
st.subheader("Pertanyaan 2: Bagaimana tren jumlah pesanan yang berhasil diselesaikan per bulan?")

delivered_df = filtered_df[filtered_df['order_status'] == 'delivered'].copy()
delivered_df['month_year'] = delivered_df['order_purchase_timestamp'].dt.to_period('M').astype(str)

monthly_orders = delivered_df.groupby('month_year')['order_id'].nunique().reset_index()

fig_trend, ax_trend = plt.subplots(figsize=(10, 4))
ax_trend.plot(monthly_orders['month_year'], monthly_orders['order_id'], marker='o', color='royalblue', linewidth=2)
ax_trend.set_title("Jumlah Pesanan Selesai per Bulan")
ax_trend.set_xlabel("Bulan")
ax_trend.set_ylabel("Jumlah Pesanan")
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.5)

st.pyplot(fig_trend)

# Insight Pertanyaan 2
st.write("**Insight:**")
st.write("- Grafik tren bulanan memperlihatkan angka pesanan yang terus merangkak naik sepanjang tahun 2017 hingga pertengahan 2018.")
st.write("- Puncak tren terjadi pada November 2017 (2017-11) dengan jumlah pesanan melonjak drastis mencapai lebih dari 7.000 transaksi.")
st.write("- Memasuki akhir tahun 2017 volume pesanan sempat sedikit menurun ke angka sekitar 5.500, namun kembali stabil di kisaran 6.000 hingga 7.000 pesanan per bulan sepanjang awal hingga pertengahan tahun 2018.")