import streamlit as st

# =========================================================
# KONFIGURASI HALAMAN STREAMLIT
# =========================================================
st.set_page_config(page_title="Penyederhanaan Boolean", layout="wide")

st.title("🎛️ Program Penyederhanaan Boolean (Kelompok 8)")
st.caption("Menggunakan Algoritma Quine-McCluskey untuk Form POS (Product of Sums)")
st.markdown("---")

# =========================================================
# TAHAP 1 & INPUT UTAMA (SIDEBAR)
# =========================================================
st.sidebar.header("📥 Input Parameter")

# Input Jumlah Variabel (Minimal 6)
jumlah_variabel = st.sidebar.number_input(
    "Masukkan jumlah variabel:", 
    min_value=6, 
    value=6, 
    step=1,
    help="Tugas Kelompok 8 mewajibkan minimal 6 variabel."
)

# Hitung batas maksimum berdasarkan 2^n
maks_nilai = (2 ** jumlah_variabel) - 1
st.sidebar.info(f"💡 Rentang desimal yang valid untuk {jumlah_variabel} variabel adalah **0 sampai {maks_nilai}**.")

# Input Maxterm
input_maxterm = st.sidebar.text_input(
    "Masukkan nilai Maxterm (Contoh: 0,1,2):",
    placeholder="0,1,2"
)

# Input Don't Care
input_dont_care = st.sidebar.text_input(
    "Masukkan nilai Don't Care (Kosongkan jika tidak ada):",
    placeholder="3,4"
)

# Tombol Eksekusi
proses_tombol = st.sidebar.button("Sederhanakan Fungsi", type="primary")

# =========================================================
# PROSES LOGIKA & VALIDASI
# =========================================================
if proses_tombol:
    # 1. Validasi Input Maxterm
    if not input_maxterm.strip():
        st.error("❌ Error: Maxterm tidak boleh kosong!")
        st.stop()
        
    try:
        daftar_maxterm = [int(x) for x in input_maxterm.split(",") if x.strip() != ""]
    except ValueError:
        st.error("❌ Error: Format Maxterm salah! Pastikan hanya berisi angka dan koma.")
        st.stop()
        
    if not all(0 <= x <= maks_nilai for x in daftar_maxterm):
        st.error(f"❌ Error: Ada angka Maxterm di luar batas rentang (0-{maks_nilai}).")
        st.stop()

    # 2. Validasi Input Don't Care
    daftar_dont_care = []
    if input_dont_care.strip():
        try:
            daftar_dont_care = [int(x) for x in input_dont_care.split(",") if x.strip() != ""]
        except ValueError:
            st.error("❌ Error: Format Don't Care salah! Pastikan hanya berisi angka dan koma.")
            st.stop()
            
        if not all(0 <= x <= maks_nilai for x in daftar_dont_care):
            st.error(f"❌ Error: Ada angka Don't Care di luar batas rentang (0-{maks_nilai}).")
            st.stop()

    # TAHAP 4 & 5: Tampilan Data Awal
    st.subheader("📋 Ringkasan Data Awal")
    col1, col2, col3 = st.columns(3)
    
    biner_maxterm = [format(angka, f'0{jumlah_variabel}b') for angka in daftar_maxterm]
    biner_dont_care = [format(angka, f'0{jumlah_variabel}b') for angka in daftar_dont_care]
    
    with col1:
        st.metric(label="Jumlah Variabel", value=jumlah_variabel)
    with col2:
        st.text(f"Daftar Maxterm Asli: {daftar_maxterm}")
        st.text(f"Biner Maxterm: {biner_maxterm}")
    with col3:
        st.text(f"Daftar Don't Care: {daftar_dont_care}")
        st.text(f"Biner Don't Care: {biner_dont_care}")
        
    st.markdown("---")

    # TAHAP 6: Tabel Tabulasi (Proses Kombinasi)
    st.subheader("📊 Proses Tabel Tabulasi")
    semua_desimal = sorted(list(set(daftar_maxterm + daftar_dont_care)))
    tabel_sekarang = [((x,), format(x, f'0{jumlah_variabel}b')) for x in semua_desimal]

    prime_implicants = set()
    kolom = 1

    while True:
        st.write(f"#### Kolom Tabulasi {kolom}")
        
        # Siapkan data untuk tabel visual Streamlit
        grup = {}
        for desimal, biner in tabel_sekarang:
            n_ones = biner.count('1')
            if n_ones not in grup:
                grup[n_ones] = []
            grup[n_ones].append((desimal, biner))

        baris_tabel = []
        for g in sorted(grup.keys()):
            for desimal, biner in grup[g]:
                nama_desimal = ", ".join(map(str, desimal))
                baris_tabel.append({
                    "Grup (Jumlah '1')": f"Grup {g}",
                    "Nilai Desimal": nama_desimal,
                    "Format Biner": biner
                })
        
        # Tampilkan tabel secara rapi di UI
        st.table(baris_tabel)

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

    # TAHAP 7: Menampilkan Prime Implicants
    st.subheader("🔍 Daftar Prime Implicants (PI)")
    list_pi = sorted(list(prime_implicants))
    for i, (desimal, biner) in enumerate(list_pi):
        nama_desimal = ", ".join(map(str, desimal))
        st.write(f"**PI {i+1}** : `{biner}` $\rightarrow$ Mencakup Desimal ({nama_desimal})")

    st.markdown("---")

    # TAHAP 8: Seleksi POS & Hasil Akhir
    maxterm_belum_tertutup = set(daftar_maxterm)
    pi_terpilih = []
    list_pi_proses = list(prime_implicants)

    while maxterm_belum_tertutup:
        terbaik_pi = None
        terbaik_cakupan = set()

        for desimal, biner in list_pi_proses:
            cakupan_maxterm = set(desimal).intersection(maxterm_belum_tertutup)
            if len(cakupan_maxterm) > len(terbaik_cakupan):
                terbaik_cakupan = cakupan_maxterm
                terbaik_pi = (desimal, biner)

        if not terbaik_pi:
            break

        pi_terpilih.append(terbaik_pi)
        maxterm_belum_tertutup -= terbaik_cakupan
        list_pi_proses.remove(terbaik_pi)

    grup_huruf_pos = []
    for desimal, biner in pi_terpilih:
        komponen_sum = []
        for i in range(jumlah_variabel):
            nama_variabel = chr(65 + i)
            if biner[i] == '0':
                komponen_sum.append(nama_variabel)
            elif biner[i] == '1':
                komponen_sum.append(f"{nama_variabel}'")

        teks_sum = f"({ ' + '.join(komponen_sum) })"
        grup_huruf_pos.append(teks_sum)

    HASIL_AKHIR_POS = "".join(grup_huruf_pos)

    # Tampilan Hasil Akhir
    st.subheader("✨ Hasil Akhir Penyederhanaan POS")
    st.success(f"**Fokus Utama Maxterm:** {daftar_maxterm}")
    st.info(f"**Hasil Akhir Y (POS):** {HASIL_AKHIR_POS}")

else:
    st.warning("👈 Silakan masukkan data di sidebar kiri, lalu klik tombol **Sederhanakan Fungsi**.")
