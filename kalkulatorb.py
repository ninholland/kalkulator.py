import streamlit as st
import pandas as pd
from itertools import combinations

# =========================================================
# KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(page_title="Kalkulator Quine McCluskey POS", layout="wide")

st.title("Program Kelompok 8: Kalkulator Quine McCluskey")
st.subheader("Penyederhanaan Fungsi Boolean (Metode POS)")
st.markdown("---")

# =========================================================
# TATA LETAK INPUT (KOLOM BIASA)
# =========================================================
# Baris Atas: Input Jumlah Variabel
jumlah_variabel = st.number_input(
    "Masukkan jumlah variabel (Minimal 6):", 
    min_value=6, 
    value=6, 
    step=1
)

# Hitung rentang maksimum
rentang = (2 ** jumlah_variabel) - 1
st.info(f"💡 Rentang maksimal desimal yang valid: **0 - {rentang}**")

# Baris Bawah: Dua Kolom Berdampingan untuk Maxterm dan Don't Care
col_input1, col_input2 = st.columns(2)

with col_input1:
    input_maxterm = st.text_input("Nilai Maxterm (Pisahkan dengan koma):", placeholder="Contoh: 0,1,2")

with col_input2:
    input_dont_care = st.text_input("Nilai Don't Care (Kosongkan jika tidak ada):", placeholder="Contoh: 3,4")

# Tombol Eksekusi di Bawah Kolom Input
st.markdown(" ")
tombol_proses = st.button("Sederhanakan Fungsi", type="primary", use_container_width=True)
st.markdown("---")

# =========================================================
# PROSES UTAMA LOGIKA QUINE-MCCLUSKEY
# =========================================================
if tombol_proses:
    # --- Validasi Maxterm ---
    if not input_maxterm.strip():
        st.error("❌ Error: Maxterm tidak boleh kosong!")
        st.stop()
        
    try:
        daftar_maxterm = [int(x) for x in input_maxterm.split(",") if x.strip() != ""]
        hasil_maks = max(daftar_maxterm)
        if hasil_maks > rentang:
            st.error(f"❌ Error: Ada maxterm yang melebihi rentang (Maksimal {rentang})!")
            st.stop()
    except ValueError:
        st.error("❌ Error: Format Maxterm salah! Pastikan hanya angka dan koma.")
        st.stop()

    # --- Validasi Don't Care ---
    daftar_dont_care = []
    if input_dont_care.strip():
        try:
            daftar_dont_care = [int(x) for x in input_dont_care.split(",") if x.strip() != ""]
            if daftar_dont_care:
                hasil_maks_dc = max(daftar_dont_care)
                if hasil_maks_dc > rentang:
                    st.error(f"❌ Error: Ada Don't Care yang melebihi rentang (Maksimal {rentang})!")
                    st.stop()
        except ValueError:
            st.error("❌ Error: Format Don't Care salah! Pastikan hanya angka dan koma.")
            st.stop()

    # --- TAHAP 4 & 5: TAMPILAN AWAL ---
    biner_maxterm = [format(angka, f'0{jumlah_variabel}b') for angka in daftar_maxterm]
    biner_dont_care = [format(angka, f'0{jumlah_variabel}b') for angka in daftar_dont_care]

    st.write("### 📋 Ringkasan Data Awal")
    col1, col2, col3 = st.columns(3)
    col1.metric("Jumlah Variabel", jumlah_variabel)
    col2.write(f"**Maxterm Asli:** {daftar_maxterm}")
    col3.write(f"**Don't Care:** {daftar_dont_care}")
    st.markdown("---")

    # --- TAHAP 6: TABEL TABULASI ---
    st.write("### 📊 Tabel Tabulasi (Proses Kombinasi)")
    semua_desimal = sorted(list(set(daftar_maxterm + daftar_dont_care)))
    tabel_sekarang = [((x,), format(x, f'0{jumlah_variabel}b')) for x in semua_desimal]

    prime_implicants = set()
    kolom = 1

    while True:
        st.write(f"**Kolom {kolom}**")
        
        grup = {}
        for desimal, biner in tabel_sekarang:
            n_ones = biner.count('1')
            if n_ones not in grup:
                grup[n_ones] = []
            grup[n_ones].append((desimal, biner))

        tabel_visual = []
        for g in sorted(grup.keys()):
            for desimal, biner in grup[g]:
                nama_desimal = ",".join(map(str, desimal))
                tabel_visual.append({"Grup": f"Grup {g}", "Nilai Desimal": nama_desimal, "Format Biner": biner})
        
        if tabel_visual:
            st.table(pd.DataFrame(tabel_visual))

        tabel_berikutnya = []
        di_eliminasi = set()

        for i in range(len(tabel_sekarang)):
            for j in range(i + 1, len(tabel_sekarang)):
                d1, b1 = tabel_sekarang[i]
                d2, b2 = tabel_sekarang[j]

                bisa_kombinasi = True
                diff = 0
                pos = -1

                for k in range(jumlah_variabel):
                    if (b1[k] == '-' and b2[k] != '-') or (b1[k] != '-' and b2[k] == '-'):
                        bisa_kombinasi = False
                        break
                    if b1[k] != b2[k]:
                        diff += 1
                        pos = k

                if bisa_kombinasi and diff == 1:
                    di_eliminasi.add(b1)
                    di_eliminasi.add(b2)
                    b_baru = list(b1)
                    b_baru[pos] = '-'
                    b_baru = "".join(b_baru)
                    d_baru = tuple(sorted(list(set(d1 + d2))))

                    if (d_baru, b_baru) not in tabel_berikutnya:
                        tabel_berikutnya.append((d_baru, b_baru))

        for d, b in tabel_sekarang:
            if b not in di_eliminasi:
                prime_implicants.add((d, b))

        if not tabel_berikutnya:
            break

        tabel_sekarang = tabel_berikutnya
        kolom += 1

    st.markdown("---")

    # --- TAHAP 7-9: TABEL CAKUPAN & PENCARIAN EPI ---
    st.write("### 🎯 Tabel Cakupan Prime Implicant (PI Chart)")
    
    list_pi = sorted(list(prime_implicants))
    target_maxterm = set(daftar_maxterm)
    target_maxterm_urut = sorted(daftar_maxterm)

    # Logika Pencarian EPI & Alternatif
    epi_terpilih = []
    sisa_maxterm = target_maxterm.copy()

    for m in target_maxterm:
        pi_pencakup = [pi for pi in list_pi if m in pi[0]]
        if len(pi_pencakup) == 1:
            if pi_pencakup[0] not in epi_terpilih:
                epi_terpilih.append(pi_pencakup[0])
                sisa_maxterm -= set(pi_pencakup[0][0])

    sisa_pi = [pi for pi in list_pi if pi not in epi_terpilih]
    kombinasi_tambahan_valid = []

    if not sisa_maxterm:
        kombinasi_tambahan_valid.append([])
    else:
        for r in range(1, len(sisa_pi) + 1):
            for kombi in combinations(sisa_pi, r):
                cakupan = set()
                for pi in kombi:
                    cakupan.update(pi[0])
                if sisa_maxterm.issubset(cakupan):
                    kombinasi_tambahan_valid.append(list(kombi))
            if kombinasi_tambahan_valid:
                break

    pi_alternatif_semua = set()
    for kombi in kombinasi_tambahan_valid:
        for pi in kombi:
            pi_alternatif_semua.add(pi)

    # Menyusun Data Frame untuk PI Chart
    pi_chart_data = []
    for desimal, biner in list_pi:
        status = ""
        if (desimal, biner) in epi_terpilih:
            status = "🌟 EPI"
        elif (desimal, biner) in pi_alternatif_semua:
            status = "✅ Alternatif"

        str_desimal = ",".join(map(str, desimal))
        baris = {
            "Status": status,
            "Nilai Desimal": str_desimal,
            "Format Biner": biner
        }
        
        for m in target_maxterm_urut:
            baris[str(m)] = "✓" if m in desimal else ""
            
        pi_chart_data.append(baris)

    df_pi_chart = pd.DataFrame(pi_chart_data)
    st.dataframe(df_pi_chart, use_container_width=True, hide_index=True)
    
    st.caption("Keterangan: 🌟 (Essential Prime Implicant) | ✅ (Alternatif Terpilih)")
    st.markdown("---")

    # --- TAHAP 10: HASIL AKHIR POS ---
    st.write("### ✨ Hasil Akhir Penyederhanaan (POS)")
    
    semua_solusi_pi = []
    for kombi in kombinasi_tambahan_valid:
        solusi_lengkap = epi_terpilih + kombi
        semua_solusi_pi.append(solusi_lengkap)

    st.success(f"Ditemukan **{len(semua_solusi_pi)}** alternatif persamaan yang paling sederhana.")

    for index, solusi in enumerate(semua_solusi_pi):
        grup_huruf_pos = []
        for desimal, biner in solusi:
            komponen_sum = []
            for i in range(jumlah_variabel):
                nama_variabel = chr(65 + i)
                if biner[i] == '0':
                    komponen_sum.append(nama_variabel)
                elif biner[i] == '1':
                    komponen_sum.append(f"{nama_variabel}'")

            teks_sum = f"({ ' + '.join(komponen_sum) })"
            grup_huruf_pos.append(teks_sum)

        hasil_akhir = "".join(grup_huruf_pos)
        st.info(f"**Alternatif {index + 1} :** F = {hasil_akhir}")

else:
    st.warning("⚠️ Silakan isi data pada form di atas, kemudian klik tombol **Sederhanakan Fungsi** untuk melihat hasil.")
