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
    
    # --- PROSES BINNING---
    bins = [0, 0.4, 0.7, 1]
    labels = ['Sangat Dingin', 'Nyaman', 'Panas']
    df['temp_category'] = pd.cut(df['temp'], bins=bins, labels=labels)
    
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
        selected_dates = st.date_input(
            label='Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
        if len(selected_dates) == 2:
            start_date, end_date = selected_dates
        else:
            st.warning("Silakan pilih rentang tanggal lengkap (Mulai & Selesai)")
            st.stop()
    except Exception as e:
        st.error(f"Terjadi kesalahan input tanggal: {e}")
        st.stop()

    # --- Filter Kategori Suhu ---
    temp_options = all_df['temp_category'].unique().tolist()
    selected_temp = st.multiselect(
        label="Pilih Kategori Suhu",
        options=temp_options,
        default=temp_options
    )

# Filtering data utama
main_df = all_df[
    (all_df["dteday"] >= pd.to_datetime(start_date)) & 
    (all_df["dteday"] <= pd.to_datetime(end_date)) &
    (all_df["temp_category"].isin(selected_temp))
]

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
    
    ax.bar(season_df['season'], season_df['registered'], label='Registered', color='#1f77b4')
    ax.bar(season_df['season'], season_df['casual'], bottom=season_df['registered'], label='Casual', color='#FFD700')
    ax.legend()
    st.pyplot(fig)

with col2:
    st.subheader("Pola Jam: Hari Kerja vs Libur")
    hourly_df = main_df.groupby(['workingday', 'hr'])['cnt'].mean().reset_index()
    hourly_df['Hari'] = hourly_df['workingday'].map({1: 'Hari Kerja', 0: 'Hari Libur'})
    
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    sns.lineplot(data=hourly_df, x='hr', y='cnt', hue='Hari', palette=['#FFD700', '#1f77b4'], ax=ax2, linewidth=3)
    ax2.set_xticks(range(0, 24))
    st.pyplot(fig2)


c_alt1, c_alt2 = st.columns(2)

# Penggunaan Berdasarkan Kategori Waktu
with c_alt1:
    st.write("#### Total Penyewaan per Kategori Waktu")
    category_summary = main_df.groupby('time_category', observed=True)['cnt'].sum().reset_index()
    
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    colors = ['#D62728' if 'Peak' in cat else '#1F77B4' for cat in category_summary['time_category']]
    
    sns.barplot(x='time_category', y='cnt', data=category_summary, palette=colors, ax=ax3)
    sns.despine() 
    for p in ax3.patches:
        ax3.annotate(f'{p.get_height():.0f}', 
                     (p.get_x() + p.get_width() / 2., p.get_height()), 
                     ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax3.set_ylabel("Total Penyewaan")
    ax3.set_xlabel("Kategori Waktu")
    st.pyplot(fig3)

# Kategori Suhu (Advanced Analysis Highlight)
with c_alt2:
    st.write("#### Efek Suhu terhadap Rata-rata Penyewaan")
    st.info("💡 **Advanced Analysis**: Mengelompokkan suhu mentah menjadi kategori persepsi manusia.")
    
    temp_analysis = main_df.groupby('temp_category', observed=True)['cnt'].mean().reset_index()
    fig_temp, ax_temp = plt.subplots(figsize=(10, 6))
    
    sns.barplot(data=temp_analysis, x='temp_category', y='cnt', palette='coolwarm', ax=ax_temp)
    sns.despine()
    
    ax_temp.set_ylabel("Rata-rata Penyewaan")
    st.pyplot(fig_temp)

st.divider()
with st.expander("Lihat Detail Kesimpulan & Rekomendasi Bisnis"):
    c1, c2 = st.columns(2)
    with c1:
        st.write("### **Insight Musiman & Pengguna**")
        st.write("""
        * **Dominasi Registered**: Pengguna loyal tetap konsisten di atas 75%.
        * **Potensi Casual**: Melonjak pada musim Summer & Fall serta pada kategori suhu **'Nyaman'** dan **'Panas'**.
        """)
    with c2:
        st.write("### **Strategi Operasional**")
        st.write("""
        * **Optimalisasi Suhu**: Pada kategori suhu 'Panas', permintaan berada di titik tertinggi. Pastikan stok sepeda penuh di lokasi wisata.
        * **Manajemen Peak**: Fokus pada jam 08:00 dan 17:00 untuk pengguna komuter.
        """)