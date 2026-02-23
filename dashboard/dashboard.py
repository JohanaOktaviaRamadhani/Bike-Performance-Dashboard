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
    return df

all_df = load_data()

# SIDEBAR
with st.sidebar:
    st.title("🚲 Bike Analysis")
    st.write(f"Halo, **Johana!**")
    
    min_date = all_df["dteday"].min()
    max_date = all_df["dteday"].max()
    
    try:
        selected_dates = st.date_input(
            label='Pilih Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
        if len(selected_dates) == 2:
            start_date, end_date = selected_dates
        else:
            start_date, end_date = min_date, max_date
    except:
        start_date, end_date = min_date, max_date

# Filter Data
main_df = all_df[(all_df["dteday"] >= pd.to_datetime(start_date)) & 
                 (all_df["dteday"] <= pd.to_datetime(end_date))]

# MAIN PAGE
st.title("📊 Bike Sharing Performance Dashboard")

# METRICS
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Total Rental", value=f"{main_df['cnt'].sum():,}")
with col_m2:
    st.metric("Registered User", value=f"{main_df['registered'].sum():,}")
with col_m3:
    st.metric("Casual User", value=f"{main_df['casual'].sum():,}")

st.divider()

col1, col2 = st.columns(2)

# CHART 1: SEASONAL ANALYSIS
with col1:
    st.subheader("Komposisi Pengguna per Musim")
    season_df = main_df.groupby('season', observed=True)[['casual', 'registered']].sum().reset_index()
    season_df['total'] = season_df['casual'] + season_df['registered']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plotting
    ax.bar(season_df['season'], season_df['registered'], label='Registered', color='#1f77b4')
    ax.bar(season_df['season'], season_df['casual'], bottom=season_df['registered'], label='Casual', color='#ff7f0e')

    for i in range(len(season_df)):
        reg_val = season_df['registered'][i]
        cas_val = season_df['casual'][i]
        total_val = season_df['total'][i]
        
        # Label Registered
        ax.text(i, reg_val/2, f"{(reg_val/total_val)*100:.1f}%", 
                ha='center', va='center', color='white', fontweight='bold', fontsize=12)
        # Label Casual
        ax.text(i, reg_val + (cas_val/2), f"{(cas_val/total_val)*100:.1f}%", 
                ha='center', va='center', color='black', fontweight='bold', fontsize=12)

    ax.set_ylabel("Total Penyewaan (Unit)")
    ax.set_title("Kontribusi Casual vs Registered", fontsize=14)
    ax.legend(loc='upper left')
    st.pyplot(fig)

# CHART 2: HOURLY PATTERN
with col2:
    st.subheader("Pola Jam: Hari Kerja vs Libur")
    hourly_df = main_df.groupby(['workingday', 'hr'])['cnt'].mean().reset_index()
    hourly_df['Hari'] = hourly_df['workingday'].map({1: 'Hari Kerja', 0: 'Hari Libur'})
    
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    sns.lineplot(
        data=hourly_df, x='hr', y='cnt', hue='Hari', 
        palette={'Hari Kerja': '#1f77b4', 'Hari Libur': '#ff7f0e'}, 
        ax=ax2, linewidth=4, marker='o'
    )
    
    ax2.set_title("Rata-rata Penyewaan per Jam", fontsize=14)
    ax2.set_xlabel("Jam (0-23)")
    ax2.set_ylabel("Rata-rata Jumlah Sepeda")
    ax2.set_xticks(range(0, 24))
    ax2.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig2)

# INSIGHT SUMMARY
with st.expander("Klik untuk Detail Kesimpulan & Jawaban Strategis"):
    st.markdown(f"""
    ### **Kesimpulan Analisis**

    #### **1. Kontribusi Pengguna per Musim (2011-2012)**
    * Perbandingan: Pengguna Registered mendominasi secara konsisten di atas 75% di semua musim (puncak loyalitas di musim Spring mencapai 87.1%).
    * Kontribusi Casual Tertinggi: Pengguna Casual paling banyak berkontribusi pada musim Fall (Gugur) secara volume, namun mencapai proporsi persentase tertinggi pada musim Summer (Panas) sebesar 22.2%. 
    Hal ini menunjukkan cuaca hangat adalah pendorong utama bagi pengguna rekreasi.

    #### **2. Pola Jam Puncak & Strategi Armada (Tahun 2012)**
    Berdasarkan data tahun 2012, terdapat kontras tajam antara hari kerja dan hari libur:
    * Puncak Hari Kerja: Terjadi pada pukul 08:00 dan 17:00–18:00, yang mengonfirmasi pola pergerakan komuter (pergi & pulang kantor).
    * Puncak Hari Libur: Terjadi secara stabil pada pukul 12:00 hingga 15:00, mencerminkan pola aktivitas rekreasi siang hari.

    #### **Strategi Distribusi Armada**
    * Hari Kerja: Fokuskan penempatan unit di area residensial sebelum jam 7 pagi dan pindahkan stok ke area perkantoran/titik transit mulai jam 4 sore.
    * Hari Libur: Distribusikan armada secara merata di area wisata, taman, dan ruang publik mulai jam 10 pagi.
    * Maintenance: Lakukan perawatan rutin pada pukul 00:00–04:00 saat permintaan berada di titik terendah untuk meminimalisir gangguan layanan.
    """)