import openpyxl
import streamlit as st
st.set_page_config(page_title="Riwayat Laptop User", layout="wide")
import pandas as pd
import plotly.express as px

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("login.py")

# Tombol logout
st.sidebar.markdown(f"👋 Hai, **{st.session_state.username}**")
if st.sidebar.button("🔓 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.switch_page("login.py")

# --- Data & App ---
def load_data():
    file_path = "data/Laptop_Riwayat.xlsx"
    laptop_data = pd.read_excel(file_path, sheet_name='Laptop Data')
    part_replacement = pd.read_excel(file_path, sheet_name='Part Replacement')
    return laptop_data, part_replacement

laptop_data, part_replacement = load_data()

merged = part_replacement.merge(laptop_data, on="User", how="left")
def convert_tanggal_ganti(val):
    try:
        # Kalau numeric, artinya serial date Excel
        if isinstance(val, (int, float)):
            return pd.to_datetime(val, origin='1899-12-30', unit='D')
        # Kalau string, coba parse langsung
        return pd.to_datetime(val, format="%Y-%m-%d", errors='coerce')
    except:
        return pd.NaT

merged["Tanggal Ganti"] = merged["Tanggal Ganti"].apply(convert_tanggal_ganti)
merged["Tahun"] = merged["Tanggal Ganti"].dt.year
merged["Bulan"] = merged["Tanggal Ganti"].dt.strftime('%Y-%m')

st.title("💻  Riwayat Laptop User")

# Filter Sidebar
st.sidebar.header("🔍 Filter Data")
selected_year = st.sidebar.selectbox("Filter berdasarkan Tahun", ["Semua"] + sorted(merged["Tahun"].dropna().unique().astype(str)))
selected_user = st.sidebar.selectbox("Filter berdasarkan User", ["Semua"] + merged["User"].unique().tolist())
selected_part = st.sidebar.selectbox("Filter berdasarkan Jenis Part", ["Semua"] + merged["Part"].unique().tolist())

filtered_data = merged.copy()
if selected_year != "Semua":
    filtered_data = filtered_data[filtered_data["Tahun"] == int(selected_year)]
if selected_user != "Semua":
    filtered_data = filtered_data[filtered_data["User"] == selected_user]
if selected_part != "Semua":
    filtered_data = filtered_data[filtered_data["Part"] == selected_part]

if st.sidebar.button("🔄 Refresh dari Excel"):
    laptop_data, part_replacement = load_data()
    st.success("Data berhasil di-refresh dari Excel.")

# Hilangkan duplikat baris jika semua kolom sama persis
filtered_data = filtered_data.drop_duplicates()

# Tampilkan data
st.subheader("📋 Daftar Spesifikasi Laptop")
st.dataframe(laptop_data)


st.subheader("📅 Riwayat Penggantian Part (Filtered)")
st.dataframe(filtered_data[["User", "Merk", "Model", "Part", "Tanggal Ganti", "Keterangan"]])

# Unduh CSV
st.subheader("⬇️ Unduh Data")
csv = filtered_data.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download CSV", csv, "riwayat_penggantian_part.csv", "text/csv")

# Visualisasi
st.subheader("🗓️ Timeline Penggantian Part")

fig_timeline = px.scatter(
    filtered_data,
    x="Tanggal Ganti",
    y="User",
    color="Part",
    symbol="Merk",
    hover_data=["Model", "Keterangan"],
    title="Timeline Riwayat Penggantian Part"
)

fig_timeline.update_traces(marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')))
fig_timeline.update_layout(
    xaxis_title="Tanggal Ganti",
    yaxis_title="User",
    hovermode="closest",
    margin=dict(t=40, b=20)
)

st.plotly_chart(fig_timeline, use_container_width=True)

st.subheader("🔩 Frekuensi Penggantian per Jenis Part")

part_count = filtered_data["Part"].value_counts().reset_index()
part_count.columns = ["Part", "Jumlah"]

fig_bar = px.bar(
    part_count,
    x="Part",
    y="Jumlah",
    color="Part",
    text="Jumlah",
    title="Jumlah Penggantian per Jenis Part"
)

fig_bar.update_traces(textposition='outside')
fig_bar.update_layout(
    xaxis_title="Jenis Part",
    yaxis_title="Jumlah",
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    margin=dict(t=40, b=20)
)

st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("📆 Tren Penggantian Part per Tahun")

yearly = filtered_data.groupby("Tahun").size().reset_index(name="Jumlah")

fig_line = px.line(
    yearly,
    x="Tahun",
    y="Jumlah",
    markers=True,
    title="Tren Penggantian Part per Tahun"
)

fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
fig_line.update_layout(
    xaxis=dict(dtick=1),
    yaxis_title="Jumlah Penggantian",
    hovermode="x unified",
    margin=dict(t=40, b=20)
)

st.plotly_chart(fig_line, use_container_width=True)


# Baris 1: CPU dan RAM
col1, col2 = st.columns(2)

with col1:
    st.subheader("🥧 Proporsi Penggunaan CPU")
    cpu_dist = laptop_data["CPU"].value_counts().reset_index()
    cpu_dist.columns = ["CPU", "Jumlah"]
    fig_cpu_pie = px.pie(
        cpu_dist,
        names="CPU",
        values="Jumlah",
        hole=0.3,
        title="Distribusi CPU"
    )
    fig_cpu_pie.update_traces(
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}",
        pull=[0.05 if i == 0 else 0 for i in range(len(cpu_dist))]
    )
    fig_cpu_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0))
    st.plotly_chart(fig_cpu_pie)

with col2:
    st.subheader("🧠 Proporsi Penggunaan RAM")
    ram_dist = laptop_data["RAM"].value_counts().reset_index()
    ram_dist.columns = ["RAM", "Jumlah"]
    fig_ram_pie = px.pie(
        ram_dist,
        names="RAM",
        values="Jumlah",
        hole=0.3,
        title="Distribusi RAM"
    )
    fig_ram_pie.update_traces(
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}",
        pull=[0.05 if i == 0 else 0 for i in range(len(ram_dist))]
    )
    fig_ram_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0))
    st.plotly_chart(fig_ram_pie)

# Baris baru: Merk Laptop & Product Release Date
col1, col2 = st.columns(2)

# 👕 Pie Chart Merk Laptop
with col1:
    st.subheader("🏷️ Proporsi Merek Laptop")
    merk_dist = laptop_data["Merk"].value_counts().reset_index()
    merk_dist.columns = ["Merk", "Jumlah"]
    fig_merk_pie = px.pie(
        merk_dist,
        names="Merk",
        values="Jumlah",
        hole=0.3,
        title="Distribusi Merek Laptop"
    )
    fig_merk_pie.update_traces(
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}",
        pull=[0.05 if i == 0 else 0 for i in range(len(merk_dist))]
    )
    fig_merk_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0))
    st.plotly_chart(fig_merk_pie)

# 🗓️ Pie Chart Product Release Date
with col2:
    st.subheader("📆 Tahun Rilis Laptop")
    prd_dist = laptop_data["Product Release Date"].value_counts().sort_index().reset_index()
    prd_dist.columns = ["Tahun Rilis", "Jumlah"]
    fig_prd_pie = px.pie(
        prd_dist,
        names="Tahun Rilis",
        values="Jumlah",
        hole=0.3,
        title="Distribusi Tahun Rilis Laptop"
    )
    fig_prd_pie.update_traces(
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}",
        pull=[0.05 if i == 0 else 0 for i in range(len(prd_dist))]
    )
    fig_prd_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0))
    st.plotly_chart(fig_prd_pie)

st.subheader("👤 Proporsi Penggantian Part per User")

user_dist = filtered_data["User"].value_counts().reset_index()
user_dist.columns = ["User", "Total"]

fig_user_pie = px.pie(
    user_dist,
    names="User",
    values="Total",
    title="Distribusi Penggantian Part per User",
    hole=0.3  # Donut style
)

fig_user_pie.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Total Penggantian: %{value}<br>Persentase: %{percent}",
    pull=[0.05 if i == 0 else 0 for i in range(len(user_dist))]  # Fokus slice pertama
)

fig_user_pie.update_layout(
    showlegend=True,
    legend_title_text="User",
    margin=dict(t=40, b=0, l=0, r=0)
)

st.plotly_chart(fig_user_pie)


st.subheader("🌡️ Heatmap Penggantian Part")

# Pivot tabel jumlah penggantian part per user
pivot = filtered_data.pivot_table(
    index="User",
    columns="Part",
    values="Tanggal Ganti",
    aggfunc="count",
    fill_value=0
)

# Interaktif Heatmap
fig_heatmap = px.imshow(
    pivot,
    text_auto=True,
    labels=dict(x="Jenis Part", y="User", color="Jumlah"),
    aspect="auto",
    title="Jumlah Penggantian Part per User",
    color_continuous_scale="YlOrRd"
)

fig_heatmap.update_layout(
    xaxis_title="Jenis Part",
    yaxis_title="User",
    margin=dict(t=50, b=20, l=20, r=20),
    coloraxis_colorbar=dict(title="Jumlah")
)

st.plotly_chart(fig_heatmap, use_container_width=True)