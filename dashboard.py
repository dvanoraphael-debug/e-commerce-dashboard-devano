import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="Dashboard Analisis Data E-Commerce", layout="wide")


# Function untuk Membaca Data
@st.cache_data
def load_data():
    dir_path = os.path.dirname(os.path.realpath(__file__))

    possible_paths = [
        os.path.join(dir_path, 'main_data.csv'),
        os.path.join(dir_path, 'dashboard', 'main_data.csv'),
        os.path.join(dir_path, 'submission', 'dashboard', 'main_data.csv'),
        'main_data.csv',
        'dashboard/main_data.csv',
        'submission/dashboard/main_data.csv'
    ]

    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break

    if file_path is None:
        raise FileNotFoundError(
            "File 'main_data.csv' tidak ditemukan di direktori utama maupun subfolder GitHub."
        )

    df = pd.read_csv(file_path)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df


try:
    df = load_data()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

# Header Dashboard
st.title("Proyek Analisis Data: E-Commerce Public Dataset (Olist)")
st.write("**Nama:** Devano Raphael Poli")
st.write("**Email:** dvanoraphael@gmail.com")
st.write("**ID Dicoding:** Devano Raphael Poli")

st.divider()

# Sidebar Filter Tanggal
st.sidebar.header("Filter Data")

min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()

date_range = st.sidebar.date_input(
    label='Rentang Waktu',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# Menangani kasus saat pengguna baru memilih satu tanggal 
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date
    st.sidebar.info("Pilih tanggal awal dan akhir untuk menerapkan filter rentang waktu.")

if start_date > end_date:
    st.sidebar.warning("Tanggal awal melebihi tanggal akhir. Menampilkan seluruh data.")
    start_date, end_date = min_date, max_date

# Filter data berdasarkan tanggal pilihan
filtered_df = df[
    (df['order_purchase_timestamp'].dt.date >= start_date) &
    (df['order_purchase_timestamp'].dt.date <= end_date)
]

# Metrik Utama
col1, col2, col3 = st.columns(3)

total_orders = filtered_df['order_id'].nunique()
total_customers = filtered_df['customer_unique_id'].nunique()
delivered_orders = filtered_df.loc[filtered_df['order_status'] == 'delivered', 'order_id'].nunique()

col1.metric("Total Orders", f"{total_orders:,}")
col2.metric("Total Customers", f"{total_customers:,}")
col3.metric("Orders Delivered", f"{delivered_orders:,}")

st.divider()

# Pertanyaan 1: Performa Penjualan Kategori Produk
st.subheader("Pertanyaan 1")
st.write(
    "Apa saja kategori produk dengan performa penjualan terbaik (pendapatan tertinggi) "
    "dan terburuk (pendapatan terendah) selama periode 2016–2018, sehingga tim bisnis dapat "
    "menentukan kategori mana yang perlu diprioritaskan promosinya dan kategori mana yang perlu "
    "dievaluasi ulang strateginya?"
)

if filtered_df.empty:
    st.warning("Tidak ada data pada rentang waktu yang dipilih.")
else:
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
st.subheader("Pertanyaan 2")
st.write(
    "Bagaimana tren jumlah pesanan (orders) yang berhasil diselesaikan oleh pelanggan pada "
    "setiap bulan selama periode 2016–2018, sehingga tim bisnis dapat menentukan bulan-bulan "
    "dengan potensi penurunan pesanan yang perlu diantisipasi dengan strategi promosi tambahan?"
)

delivered_df = filtered_df[filtered_df['order_status'] == 'delivered'].copy()

if delivered_df.empty:
    st.warning("Tidak ada pesanan delivered pada rentang waktu yang dipilih.")
else:
    delivered_df['month_year'] = delivered_df['order_purchase_timestamp'].dt.to_period('M').astype(str)

    monthly_orders = (
        delivered_df.groupby('month_year')['order_id']
        .nunique()
        .reset_index()
        .sort_values(by='month_year')
    )

    fig_trend, ax_trend = plt.subplots(figsize=(10, 4))
    ax_trend.plot(monthly_orders['month_year'], monthly_orders['order_id'], marker='o', color='royalblue', linewidth=2)
    ax_trend.set_title("Jumlah Pesanan Selesai per Bulan")
    ax_trend.set_xlabel("Bulan")
    ax_trend.set_ylabel("Jumlah Pesanan")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    st.pyplot(fig_trend)

    # Insight Pertanyaan 2
    st.write("**Insight:**")
    st.write("- Grafik tren bulanan memperlihatkan angka pesanan yang terus merangkak naik sepanjang tahun 2017 hingga pertengahan 2018.")
    st.write("- Puncak tren terjadi pada November 2017 (2017-11) dengan jumlah pesanan melonjak drastis mencapai lebih dari 7.000 transaksi.")
    st.write("- Memasuki akhir tahun 2017 volume pesanan sempat sedikit menurun ke angka sekitar 5.500, namun kembali stabil di kisaran 6.000 hingga 7.000 pesanan per bulan sepanjang awal hingga pertengahan tahun 2018.")

st.divider()

# Analisis Lanjutan: Segmentasi Pelanggan (RFM)
st.subheader("Analisis Lanjutan: Segmentasi Pelanggan (RFM)")
st.caption(
    "Recency dihitung relatif terhadap tanggal transaksi terakhir pada rentang waktu yang "
    "sedang difilter di sidebar."
)

rfm_source_df = filtered_df.dropna(subset=['customer_unique_id', 'order_purchase_timestamp'])

if rfm_source_df['customer_unique_id'].nunique() < 5:
    st.warning("Data pelanggan pada rentang waktu ini terlalu sedikit untuk dibuat segmentasi RFM.")
else:
    max_order_date = rfm_source_df['order_purchase_timestamp'].max()

    rfm_df = rfm_source_df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": lambda x: (max_order_date - x.max()).days,  # Recency (hari)
        "order_id": "nunique",  # Frequency (jumlah transaksi)
        "price": "sum"  # Monetary (total pengeluaran)
    })
    rfm_df.columns = ["customer_unique_id", "recency", "frequency", "monetary"]

    try:
        # --- Scoring RFM (skor 1-5 per dimensi) ---
        # Recency: semakin kecil nilainya semakin baik (skor 5 = paling baru bertransaksi)
        rfm_df['r_score'] = pd.qcut(rfm_df['recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop').astype(int)
        # Frequency & Monetary: semakin besar nilainya semakin baik (skor 5 = paling tinggi)
        rfm_df['f_score'] = pd.qcut(rfm_df['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
        rfm_df['m_score'] = pd.qcut(rfm_df['monetary'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop').astype(int)

        # --- Segmentasi pelanggan berdasarkan kombinasi skor RFM ---
        def segmentasi_rfm(row):
            r, f, m = row['r_score'], row['f_score'], row['m_score']
            if r >= 4 and f >= 4 and m >= 4:
                return 'Champions'
            elif r >= 3 and f >= 3:
                return 'Loyal Customers'
            elif r >= 4 and f <= 2:
                return 'New Customers'
            elif r <= 2 and f >= 3:
                return 'At Risk'
            elif r <= 2 and f <= 2 and m <= 2:
                return 'Lost Customers'
            else:
                return 'Potential Loyalist'

        rfm_df['segment'] = rfm_df.apply(segmentasi_rfm, axis=1)

        col_rfm1, col_rfm2 = st.columns([2, 3])

        with col_rfm1:
            st.write("**Top 5 Pelanggan Berdasarkan Frekuensi Belanja**")
            st.dataframe(
                rfm_df.sort_values(by="frequency", ascending=False)
                .head(5)[["customer_unique_id", "recency", "frequency", "monetary", "segment"]],
                width='stretch',
                hide_index=True
            )

        with col_rfm2:
            segment_counts = rfm_df['segment'].value_counts().sort_values(ascending=True)

            fig_rfm, ax_rfm = plt.subplots(figsize=(8, 4.5))
            sns.barplot(
                x=segment_counts.values, y=segment_counts.index,
                hue=segment_counts.index, palette="viridis", legend=False, ax=ax_rfm
            )
            ax_rfm.set_title("Distribusi Jumlah Pelanggan Berdasarkan Segmen RFM", fontsize=13)
            ax_rfm.set_xlabel("Jumlah Pelanggan")
            ax_rfm.set_ylabel("")
            plt.tight_layout()
            st.pyplot(fig_rfm)

        # Insight RFM
        st.write("**Insight:**")
        st.write("- Setiap pelanggan diberi skor 1–5 pada tiga dimensi (recency, frequency, monetary), lalu dikelompokkan menjadi segmen Champions, Loyal Customers, Potential Loyalist, New Customers, At Risk, dan Lost Customers berdasarkan kombinasi skornya.")
        st.write("- Segmen **Champions** dan **Loyal Customers** adalah aset utama yang perlu dipertahankan melalui program loyalitas atau reward khusus.")
        st.write("- Segmen **At Risk** dan **Lost Customers** perlu menjadi target reaktivasi lewat kampanye pemasaran agar kembali aktif bertransaksi di platform.")

    except ValueError:
        st.warning(
            "Variasi data pada rentang waktu ini terlalu kecil untuk membagi pelanggan ke dalam "
            "5 kelompok skor. Coba perluas rentang tanggal pada filter."
        )