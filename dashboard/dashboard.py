import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(layout="wide", page_title="Bike Sharing Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    df['dteday'] = pd.to_datetime(df['dteday'])
    return df

all_df = load_data()

with st.sidebar:
    st.title("🚲 Bike Analysis")
    st.write("Halo, Johana!")
    
    min_date = all_df["dteday"].min()
    max_date = all_df["dteday"].max()
    
    try:
        start_date, end_date = st.date_input(
            label='Pilih Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    except:
        start_date, end_date = min_date, max_date

main_df = all_df[(all_df["dteday"] >= pd.to_datetime(start_date)) & 
                 (all_df["dteday"] <= pd.to_datetime(end_date))]

st.title("Bike Sharing Performance Dashboard")

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Total Rental", value=f"{main_df['cnt'].sum():,}")
with col_m2:
    st.metric("Registered", value=f"{main_df['registered'].sum():,}")
with col_m3:
    st.metric("Casual", value=f"{main_df['casual'].sum():,}")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Casual vs Registered per Musim")
    season_df = main_df.groupby('season')[['casual', 'registered']].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.bar(season_df['season'], season_df['registered'], label='Registered', color='#1E90FF')
    ax.bar(season_df['season'], season_df['casual'], bottom=season_df['registered'], label='Casual', color='#FFD700')
    
    ax.set_ylabel("Rata-rata Penyewaan")
    ax.legend()
    st.pyplot(fig)

with col2:
    st.subheader("Pola Jam: Hari Kerja vs Libur")
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    
    sns.lineplot(
        data=main_df, x='hr', y='cnt', hue='workingday', 
        palette={1: '#1E90FF', 0: '#FFD700'}, ax=ax2, linewidth=3
    )
    ax2.set_xlabel("Jam")
    ax2.set_ylabel("Total Penyewaan")
    ax2.legend(["Libur (Kuning)", "Hari Kerja (Biru)"])
    st.pyplot(fig2)

with st.expander("Lihat Kesimpulan"):
    st.write("""
    - 1. Dinamika Pengguna Berdasarkan Musim Kontribusi pengguna Casual melonjak signifikan pada musim Fall 
        dan Summer, menunjukkan bahwa cuaca hangat menjadi pendorong utama aktivitas rekreasi dibandingkan musim lainnya.
    - 2. Perbandingan Pola Jam Hari Kerja vs Libur: Aktivitas penyewaan pada hari kerja didominasi pola komuter 
        dengan puncak tajam di jam berangkat (08:00) dan pulang kantor (17:00), sedangkan pada hari libur beralih 
        ke pola rekreasi yang lebih stabil dengan titik tertinggi di siang hari pukul 12:00 hingga 15:00.
    - 3. Strategi Distribusi Armada : Armada sebaiknya difokuskan pada area residensial dan perkantoran saat hari kerja, 
        namun segera dialihkan ke area wisata atau ruang publik saat akhir pekan guna mengantisipasi perbedaan puncak jam penyewaan tersebut.
        """)