import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(layout="wide", page_title="Bike Sharing Dashboard")
sns.set_style("whitegrid")

@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    df['dteday'] = pd.to_datetime(df['dteday'])
    
    season_order = ['Spring', 'Summer', 'Fall', 'Winter']
    df['season'] = pd.Categorical(df['season'], categories=season_order, ordered=True)
    
    time_order = ['Morning Peak', 'Mid-day', 'Evening Peak', 'Off-peak/Night']
    df['time_category'] = pd.Categorical(df['time_category'], categories=time_order, ordered=True)
    
    return df

all_df = load_data()

with st.sidebar:
    st.title("🚲 Bike Analysis")
    st.write(f"Halo, **Johana!**")
    min_date, max_date = all_df["dteday"].min(), all_df["dteday"].max()
    try:
        selected_dates = st.date_input(label='Rentang Waktu', min_value=min_date, max_value=max_date, value=[min_date, max_date])
        start_date, end_date = selected_dates if len(selected_dates) == 2 else (min_date, max_date)
    except:
        start_date, end_date = min_date, max_date

main_df = all_df[(all_df["dteday"] >= pd.to_datetime(start_date)) & (all_df["dteday"] <= pd.to_datetime(end_date))]

st.title("📊 Bike Sharing Performance Dashboard")
m1, m2, m3 = st.columns(3)
m1.metric("Total Rental", f"{main_df['cnt'].sum():,}")
m2.metric("Registered", f"{main_df['registered'].sum():,}")
m3.metric("Casual", f"{main_df['casual'].sum():,}")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Komposisi Pengguna per Musim")
    season_df = main_df.groupby('season', observed=True)[['casual', 'registered']].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Biru untuk Registered, Kuning untuk Casual
    ax.bar(season_df['season'], season_df['registered'], label='Registered', color='#1f77b4')
    ax.bar(season_df['season'], season_df['casual'], bottom=season_df['registered'], label='Casual', color='#FFD700')
    ax.legend()
    st.pyplot(fig)

with col2:
    st.subheader("Pola Jam: Hari Kerja vs Libur")
    hourly_df = main_df.groupby(['workingday', 'hr'])['cnt'].mean().reset_index()
    hourly_df['Hari'] = hourly_df['workingday'].map({1: 'Hari Kerja', 0: 'Hari Libur'})
    
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    # Palette Biru dan Kuning
    sns.lineplot(data=hourly_df, x='hr', y='cnt', hue='Hari', palette=['#FFD700', '#1f77b4'], ax=ax2, linewidth=3)
    ax2.set_xticks(range(0, 24))
    st.pyplot(fig2)

st.divider()
st.subheader("Analisis Berdasarkan Kategori Waktu")

category_summary = main_df.groupby('time_category', observed=True)['cnt'].mean().reset_index()
fig3, ax3 = plt.subplots(figsize=(12, 5))
# Highlight Peak dengan Biru, lainnya Kuning
colors = ['#1f77b4' if 'Peak' in cat else '#FFD700' for cat in category_summary['time_category']]

sns.barplot(x='time_category', y='cnt', data=category_summary, palette=colors, ax=ax3)

for p in ax3.patches:
    ax3.annotate(f'{p.get_height():.0f}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom')

st.pyplot(fig3)
st.divider()
with st.expander("Lihat Detail Kesimpulan & Rekomendasi Bisnis"):
    c1, c2 = st.columns(2)
    with c1:
        st.write("### **Insight Musiman & Pengguna**")
        st.write("""
        * Dominasi Biru (Registered): Pengguna loyal tetap menjadi tulang punggung bisnis dengan kontribusi konsisten di atas 75% di semua musim.
        * Potensi Kuning (Casual):Kontribusi tertinggi pengguna Casual terlihat pada musim Summer & Fall. Ini adalah momen tepat untuk menawarkan daily pass atau promo rekreasi.
        """)
    with c2:
        st.write("### **Strategi Operasional & Waktu**")
        st.write("""
        * Manajemen Peak (Biru): Grafik menunjukkan lonjakan tajam pada jam berangkat (08:00) dan pulang kantor (17:00). Pastikan ketersediaan sepeda maksimal di titik transit pada jam tersebut.
        * Manajemen Mid-day (Kuning): Pada hari libur, penyewaan terpusat di tengah hari. Distribusi armada harus digeser ke area taman dan pusat hiburan mulai pukul 10:00 pagi.
        """)