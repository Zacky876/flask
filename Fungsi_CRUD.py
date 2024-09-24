import qrcode, string, random
import os
from tabulate import tabulate
from flask import request, render_template, redirect, url_for, flash, Flask, session, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'zangetsu88'
db_path = r"C:\Users\ASUS\OneDrive\Documents\PYTHON\LATIHAN PYTHON\akademik.db"

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Ambil role pengguna dari database
        try:
            con = sqlite3.connect(db_path)
            cur = con.cursor()

            # Cek login sebagai siswa
            cur.execute("SELECT * FROM data_siswa WHERE NIS = ? AND password = ?", (username, password))
            siswa = cur.fetchone()

            if siswa:
                session['username'] = username
                session['role'] = 'murid'
                session['nis'] = siswa[0]
                
                cur.execute("SELECT nama_siswa FROM data_siswa WHERE NIS = ?", (siswa[0],))
                nama_siswa = cur.fetchone()[0]

                session['nama_siswa'] = nama_siswa
                return redirect(url_for('murid_bp.halaman_siswa'))
            
            # Cek login sebagai guru
            cur.execute("SELECT nama_guru FROM data_guru WHERE nama_guru = ? AND password = ?", (username, password))
            guru = cur.fetchone()

            if guru:
                session['username'] = username
                session['role'] = 'guru'
                session['nama_guru'] = guru[0]  # Ini harusnya nama guru
                return redirect(url_for('guru_bp.halaman_guru'))
            
            # Cek login sebagai admin
            cur.execute("SELECT * FROM login WHERE username = ? AND password = ?", (username, password))
            admin = cur.fetchone()

            if admin:
                session['username'] = username
                session['role'] = 'admin'  # Set role di session
                return redirect(url_for('admin_bp.halaman_admin'))

            # Jika login gagal
            return render_template('login.html', error='Username atau password salah.')

        except sqlite3.Error as e:
            print(f"Login gagal: {e}")
            return render_template('login.html', error='Terjadi kesalahan pada server.')

        finally:
            if con:
                con.close()

    return render_template('login.html')

def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

def generate_random_code(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def check_database():
    db_path = input(f"Masukan Nama Database:")
    if os.path.exists(db_path):
        try:
            con = sqlite3.connect(db_path)
            print("Database ada.")
            con.close()
        except sqlite3.Error as e:
            print(f"File ada, tetapi bukan database SQLite: {e}")
    else:
        print("Database tidak ada.")


def tampilkan_siswa(page_title):
    con = None
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        query = '''
            SELECT Data_siswa.NIS, kelas.nama_kelas, Data_siswa.nama_siswa, 
                   Data_siswa.jenis_kelamin, Data_siswa.tempat_lahir, 
                   Data_siswa.tanggal_lahir, Data_siswa.agama, 
                   Data_siswa.alamat, Data_siswa.orang_tua
            FROM Data_siswa 
            JOIN kelas ON Data_siswa.id_kelas = kelas.id_kelas
        '''
        cur.execute(query)
        rows = cur.fetchall()

        if rows:
            return render_template('murid/tampilkan_siswa.html', rows=rows, page_title=page_title)
        else:
            return "Tidak ada data siswa."

    except sqlite3.Error as e:
        return f"Error saat mengambil data dari database: {e}"

    finally:
        if con:
            con.close()


def tampilkan_guru(page_title):
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        query = '''
            SELECT *
            FROM Data_guru
        '''
        cur.execute(query)
        rows = cur.fetchall()

        if rows:
            return render_template('guru/tampilkan_guru.html', rows=rows, page_title=page_title)
        else:
            return "Tidak ada data guru."  # Perbaiki pesan ini

    except sqlite3.Error as e:
        return f"Error saat mengambil data dari database: {e}"

    finally:
        if con:
            con.close()

def tambah_siswa(page_title):
    if request.method == 'POST':
        try:
            # Mengambil data dari form
            nama = request.form['nama']
            id_kelas = int(request.form['id_kelas'])
            jenis_kelamin = request.form['jenis_kelamin']
            tempat_tinggal = request.form['tempat_tinggal']
            tanggal_lahir = request.form['tanggal_lahir']
            agama = request.form['agama']
            alamat = request.form['alamat']
            nama_ortu = request.form['nama_ortu']

            # Membuka koneksi ke database
            con = sqlite3.connect(db_path)
            cur = con.cursor()

            # Memeriksa apakah ID kelas ada
            cur.execute("SELECT COUNT(*) FROM kelas WHERE id_kelas = ?", (id_kelas,))
            if cur.fetchone()[0] == 0:
                flash(f"ID kelas {id_kelas} tidak ditemukan di tabel kelas.")
                return redirect(url_for('admin/tambah_siswa'))

            # Menambahkan data siswa baru
            query = '''
                INSERT INTO Data_siswa (nama_siswa, id_kelas, jenis_kelamin, tempat_lahir, 
                tanggal_lahir, agama, alamat, orang_tua) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            cur.execute(query, (nama, id_kelas, jenis_kelamin, tempat_tinggal, tanggal_lahir, agama, alamat, nama_ortu))
            con.commit()

            flash(f"Siswa {nama} berhasil ditambahkan ke dalam database.")
            return redirect(url_for('murid/tampilkan_siswa'))

        except sqlite3.Error as e:
            flash(f"Error saat mengirim data ke database: {e}")
            return redirect(url_for('admin/tambah_siswa'))
        
        finally:
            if con:
                con.close()

    # Jika metode bukan POST, tampilkan form input
    return render_template('admin/tambah_siswa.html', page_title=page_title)

def tambah_guru(page_title):
    if request.method == 'POST':
        on = None  # Deklarasikan variabel sebelum blok try

        try:
            on = sqlite3.connect(db_path)
            cur = on.cursor()

            # Mengambil data dari form
            nama = request.form['nama']
            jenis_kelamin = request.form['jenis_kelamin']
            tempat_tinggal = request.form['tempat_tinggal']
            tanggal_lahir = request.form['tanggal_lahir']
            agama = request.form['agama']
            alamat = request.form['alamat']

            # Memasukkan data guru ke tabel
            query = '''
                INSERT INTO Data_guru 
                (nama_guru, jenis_kelamin, tempat_lahir, tanggal_lahir, agama, alamat) 
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            cur.execute(query, (nama, jenis_kelamin, tempat_tinggal, tanggal_lahir, agama, alamat))
            on.commit()

            flash(f"Guru {nama} berhasil ditambahkan ke dalam database.", "success")
            return redirect(url_for('guru/tampilkan_guru'))

        except sqlite3.Error as e:
            flash(f"Error saat mengirim data ke database: {e}", "danger")
            return redirect(url_for('admin/tambah_guru'))

        finally:
            if on:  # Pastikan 'on' telah didefinisikan sebelum menutup
                on.close()
                
    # Jika metode bukan POST, tampilkan form input
    return render_template('admin/tambah_guru.html', page_title=page_title)

def hapus_siswa(page_title):
    if request.method == 'POST':
        con = None  # Deklarasikan variabel sebelum blok try

        try:
            con = sqlite3.connect(db_path)
            cur = con.cursor()

            siswa_id = int(request.form['id_siswa'])

            cur.execute("SELECT COUNT(*) FROM Data_siswa WHERE NIS = ?", (siswa_id,))
            if cur.fetchone()[0] == 0:
                flash(f"Siswa dengan ID {siswa_id} tidak ditemukan di dalam database.", "warning")
                return redirect(url_for('admin/hapus_siswa'))  # Redirect ke halaman hapus_siswa jika siswa tidak ditemukan

            query = "DELETE FROM Data_siswa WHERE NIS = ?"
            cur.execute(query, (siswa_id,))
            con.commit()

            flash(f"Siswa dengan ID {siswa_id} berhasil dihapus dari database.", "success")
            return redirect(url_for('murid/tampilkan_siswa'))  # Redirect ke halaman tampilkan_siswa setelah penghapusan

        except sqlite3.Error as e:
            flash(f"Error saat menghapus data dari database: {e}", "danger")
            return redirect(url_for('admin/hapus_siswa'))  # Redirect jika terjadi error

        finally:
            if con:  # Pastikan 'con' telah didefinisikan sebelum menutup
                con.close()

    # Jika metode bukan POST, tampilkan form input
    return render_template('admin/hapus_siswa.html', page_title=page_title)


def hapus_guru(page_title):
    if request.method == 'POST':
        try:

            con = sqlite3.connect(db_path)
            cur = con.cursor()

            id = int(request.form['id_guru'])

            cur.execute("SELECT COUNT(*) FROM data_guru WHERE id_guru = ?", (id,))
            if cur.fetchone()[0] == 0:
                print(f"Siswa dengan ID {id} tidak ditemukan di dalam database.")
                return redirect(url_for('admin/hapus_guru'))

            query = "DELETE FROM Data_guru WHERE id_guru = ?"
            cur.execute(query, (id,))
            con.commit()

            print(f"Siswa dengan ID {id} berhasil dihapus dari database.")
            return redirect(url_for('guru/tampilkan_guru')) 

        except sqlite3.Error as e:
            print(f"Error saat menghapus data dari database: {e}")
            return redirect(url_for('admin/hapus_siswa'))
        finally:
            con.close()
    return render_template('admin/hapus_guru.html', page_title=page_title)

def update_siswa(page_title):
    if request.method == 'POST':
        try:
            con = sqlite3.connect(db_path)
            cur = con.cursor()

            # Mengambil data dari form
            siswa_id = request.form.get('NIS')
            nama = request.form.get('nama_siswa')
            jenis_kelamin = request.form.get('jenis_kelamin')
            tempat_lahir = request.form.get('tempat_lahir')
            tanggal_lahir = request.form.get('tanggal_lahir')
            agama = request.form.get('agama')
            alamat = request.form.get('alamat')
            orang_tua = request.form.get('orang_tua')

            # Validasi ID Siswa
            if not siswa_id or not siswa_id.isdigit():
                flash('ID Siswa tidak valid atau tidak diisi. Silakan coba lagi.', 'danger')
                return redirect(url_for('admin/update_siswa'))
            
            siswa_id = int(siswa_id)

            # Validasi apakah siswa dengan ID tersebut ada di database
            cur.execute("SELECT COUNT(*) FROM Data_siswa WHERE NIS = ?", (siswa_id,))
            if cur.fetchone()[0] == 0:
                flash(f"Siswa dengan ID {siswa_id} tidak ditemukan di dalam database.", 'danger')
                return redirect(url_for('admin/update_siswa'))

            # Membuat query update secara dinamis
            update_query = "UPDATE Data_siswa SET "
            update_values = []

            if nama:
                update_query += "nama_siswa = ?, "
                update_values.append(nama)

            if jenis_kelamin:
                update_query += "jenis_kelamin = ?, "
                update_values.append(jenis_kelamin)

            if tempat_lahir:
                update_query += "tempat_lahir = ?, "
                update_values.append(tempat_lahir)

            if tanggal_lahir:  # Pastikan untuk menambahkan ini jika diperlukan
                update_query += "tanggal_lahir = ?, "
                update_values.append(tanggal_lahir)

            if agama:
                update_query += "agama = ?, "
                update_values.append(agama)

            if alamat:
                update_query += "alamat = ?, "
                update_values.append(alamat)

            if orang_tua:
                update_query += "orang_tua = ?, "
                update_values.append(orang_tua)

            # Menghapus koma terakhir dan menambahkan WHERE
            if update_values:
                update_query = update_query.rstrip(", ") + " WHERE NIS = ?"
                update_values.append(siswa_id)

                # Debug: Print query dan values (hapus atau komentari jika tidak diperlukan)
                # print("Query SQL:", update_query)
                # print("Values:", update_values)

                # Menjalankan query update
                cur.execute(update_query, update_values)

                # Commit perubahan ke database
                con.commit()
                flash(f"Data siswa dengan ID {siswa_id} berhasil diupdate.", 'success')
            else:
                flash("Tidak ada data yang diupdate. Silakan isi form dengan benar.", 'warning')

            return redirect(url_for('murid/tampilkan_siswa'))

        except sqlite3.Error as e:
            error_msg = str(e)
            # Log error ke console, jika tidak diperlukan hapus atau komentari
            # print("Error saat mengupdate data:", error_msg)
            flash(f"Error saat mengupdate data di database: {error_msg}", 'danger')
            return redirect(url_for('admin/update_siswa'))
        finally:
            if con:
                con.close()
    return render_template('admin/update_siswa.html', page_title=page_title)


def update_guru(page_title):
    if request.method == 'POST':
        try:
            con = sqlite3.connect(db_path)
            cur = con.cursor()

            # Mengambil data dari form
            id_guru = request.form.get('id_guru')
            nama = request.form.get('nama_guru')
            jenis_kelamin = request.form.get('jenis_kelamin')
            tempat_lahir = request.form.get('tempat_lahir')
            tanggal_lahir = request.form.get('tanggal_lahir')
            agama = request.form.get('agama')
            alamat = request.form.get('alamat')

            # Validasi ID Guru
            if not id_guru or not id_guru.isdigit():
                flash('ID Guru tidak valid atau tidak diisi. Silakan coba lagi.', 'danger')
                return redirect(url_for('admin/update_guru'))
            
            id_guru = int(id_guru)

            # Validasi apakah Guru dengan ID tersebut ada di database
            cur.execute("SELECT COUNT(*) FROM Data_guru WHERE id_guru = ?", (id_guru,))
            if cur.fetchone()[0] == 0:
                flash(f"Guru dengan ID {id_guru} tidak ditemukan di dalam database.", 'danger')
                return redirect(url_for('admin/update_guru'))

            update_query = "UPDATE Data_guru SET "
            update_values = []

            if nama:
                update_query += "nama_guru = ?, "
                update_values.append(nama)

            if jenis_kelamin:
                update_query += "jenis_kelamin = ?, "
                update_values.append(jenis_kelamin)

            if tempat_lahir:
                update_query += "tempat_lahir = ?, "
                update_values.append(tempat_lahir)

            if tanggal_lahir:  # Pastikan untuk menambahkan ini jika diperlukan
                update_query += "tanggal_lahir = ?, "
                update_values.append(tanggal_lahir)

            if agama:
                update_query += "agama = ?, "
                update_values.append(agama)

            if alamat:
                update_query += "alamat = ?, "
                update_values.append(alamat)

            # Menghapus koma terakhir dan menambahkan WHERE
            if update_values:
                update_query = update_query.rstrip(", ") + " WHERE id_guru = ?"
                update_values.append(id_guru)

                # Menjalankan query update
                cur.execute(update_query, update_values)

                # Commit perubahan ke database
                con.commit()
                flash(f"Data guru dengan ID {id_guru} berhasil diupdate.", 'success')
            else:
                flash("Tidak ada data yang diupdate. Silakan isi form dengan benar.", 'warning')

            return redirect(url_for('guru/tampilkan_guru'))

        except sqlite3.Error as e:
            error_msg = str(e)
            flash(f"Error saat mengupdate data di database: {error_msg}", 'danger')
            return redirect(url_for('admin/update_guru'))
        finally:
            if con:
                con.close()
    return render_template('admin/update_guru.html', page_title=page_title)


def tampilkan_jadwal_siswa(page_title):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT jadwal.id_jadwal, kelas.nama_kelas, Data_guru.nama_guru, mapel.nama_pelajaran, jadwal.hari, jadwal.jam_mapel
        FROM jadwal
        JOIN Data_guru ON jadwal.id_guru = Data_guru.id_guru
        JOIN mapel ON jadwal.id_mapel = mapel.id_mapel
        JOIN kelas ON jadwal.id_kelas = kelas.id_kelas
        ORDER BY id_jadwal 
        """)
        
        jadwal = cursor.fetchall()
        
        if jadwal:
            return render_template('murid/tampilkan_jadwal.html', jadwal=jadwal, page_title=page_title)
        else:
            return render_template('murid/tampilkan_jadwal.html', table=None, error="Tidak ada jadwal ditemukan.")
       
    except sqlite3.Error as e:
        return render_template('murid/tampilkan_jadwal.html', table=None, error=f"Error saat mengakses database: {e}")
        
    finally:
        if conn:
            conn.close()

def Tampilkan_data(tahun, page_title):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Menggunakan LIKE untuk mencocokkan tahun kelahiran
        cur.execute("""
        SELECT Data_siswa.NIS, kelas.nama_kelas, Data_siswa.nama_siswa, Data_siswa.jenis_kelamin, 
               Data_siswa.tempat_lahir, Data_siswa.tanggal_lahir, Data_siswa.agama, Data_siswa.alamat, 
               Data_siswa.orang_tua
        FROM Data_siswa
        JOIN kelas ON Data_siswa.id_kelas = kelas.id_kelas
        WHERE strftime('%Y', Data_siswa.tanggal_lahir) = ?
        """, (tahun,))
        
        siswa = cur.fetchall()
        
        if siswa:
            return render_template('admin/tampilkan_pertahun.html', siswa=siswa, page_title=page_title)
        else:
            return render_template('admin/tampilkan_pertahun.html', siswa=None, error=f"Tidak ada siswa dengan tahun {tahun} tersebut.")
            
    except sqlite3.Error as e:
        print(f"Error saat mengakses database: {e}")
        return render_template('admin/tampilkan_pertahun.html', siswa=None, error=f"Error saat mengakses database: {e}")
        
    finally:
        if conn:
            conn.close()

def tampilkan_jadwal(siswa, page_title):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute("""
        SELECT Data_siswa.NIS, Data_siswa.nama_siswa, kelas.id_kelas, jadwal.hari, jadwal.jam_mapel, 
               Data_guru.nama_guru, mapel.nama_pelajaran
        FROM Data_siswa
        JOIN kelas ON Data_siswa.id_kelas = kelas.id_kelas
        JOIN jadwal ON kelas.id_kelas = jadwal.id_kelas
        JOIN Data_guru ON jadwal.id_guru = Data_guru.id_guru
        JOIN mapel ON jadwal.id_mapel = mapel.id_mapel
        WHERE Data_siswa.nama_siswa = ?
        ORDER BY jadwal.hari, jadwal.jam_mapel;
        """, (siswa,))
        
        jadwal = cur.fetchall()
        
        if jadwal:
            return render_template('admin/tampilkan_perhari.html', jadwal=jadwal, page_title=page_title)
        else:
            return render_template('admin/tampilkan_perhari.html', jadwal=None, error=f"Tidak ada jadwal untuk siswa dengan nama {siswa}.")
            
    except sqlite3.Error as e:
        return render_template('admin_bp.tampilkan_perhari.html', jadwal=None, error=f"Error saat mengakses database: {e}")
        
    finally:
        if conn:
            conn.close()

def jumlah_jam_mapel(bulan, jenis_kelamin, pelajaran, page_title):
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()

            # Query SQL untuk mengambil data sesuai dengan input
            cur.execute("""
            SELECT Data_siswa.NIS, Data_siswa.nama_siswa, kelas.nama_kelas, jadwal.hari, jadwal.jam_mapel, 
                   Data_guru.nama_guru, mapel.nama_pelajaran
            FROM Data_siswa
            JOIN kelas ON Data_siswa.id_kelas = kelas.id_kelas
            JOIN jadwal ON kelas.id_kelas = jadwal.id_kelas
            JOIN Data_guru ON jadwal.id_guru = Data_guru.id_guru
            JOIN mapel ON jadwal.id_mapel = mapel.id_mapel
            WHERE Data_siswa.jenis_kelamin = ?
            AND mapel.nama_pelajaran = ?
            AND strftime('%m', Data_siswa.tanggal_lahir) = ?
            ORDER BY jadwal.hari, jadwal.jam_mapel;
            """, (jenis_kelamin, pelajaran, bulan))

            siswa = cur.fetchall()

            # Memeriksa apakah ada data siswa yang ditemukan
            if siswa:
                return render_template('admin/tampilkan_jam_mapel.html', siswa=siswa, page_title=page_title)
            else:
                return render_template('admin/tampilkan_jam_mapel.html', siswa=None, error=f"Tidak ada siswa {jenis_kelamin} yang belajar {pelajaran} dan lahir pada bulan {bulan}.")
                
    except sqlite3.Error as e:
        # Menangani error database dan memberikan feedback yang tepat
        return render_template('admin_bp.tampilkan_jam_mapel.html', siswa=None, error=f"Terjadi kesalahan saat mengakses database: {e}")

    finally:
        if conn:
            conn.close()

def export_jadwal(id_kelas):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT nama_kelas FROM kelas WHERE id_kelas = ?", (id_kelas,))
        kelas_row = cursor.fetchone()

        # Jika kelas tidak ditemukan, return dengan pesan error
        if not kelas_row:
            return None, [], "Kelas tidak ditemukan."

        # Menyimpan nama kelas yang ditemukan
        nama_kelas = kelas_row[0]

        list_waktu = [
            '07.15 - 08.00', '08.00 - 08.45', '08.45 - 09.30',
            '09.30 - 10.15', '10.15 - 11.00', '11.00 - 11.45',
            '11.45 - 12.30', '12.30 - 13.15', '13.15 - 14.00',
            '14.00 - 14.45'
        ]

        cursor.execute("""
        SELECT jadwal.hari, jadwal.jam_mapel, mapel.nama_pelajaran, Data_guru.nama_guru
        FROM jadwal
        JOIN Data_guru ON jadwal.id_guru = Data_guru.id_guru
        JOIN mapel ON jadwal.id_mapel = mapel.id_mapel
        WHERE jadwal.id_kelas = ?
        ORDER BY jadwal.hari, jadwal.jam_mapel
        """, (id_kelas,))

        hasil_jadwal = cursor.fetchall()

        if not hasil_jadwal:
            return nama_kelas, [], "Tidak ada jadwal tersedia untuk kelas ini."

        jadwal = []

        for hari, jam_mapel, nama_pelajaran, nama_guru in hasil_jadwal:
            # Mendapatkan waktu yang sesuai berdasarkan indeks
            waktu = list_waktu[(jam_mapel - 1) % len(list_waktu)]
            # Menambahkan data ke list jadwal
            jadwal.append((hari, jam_mapel, waktu, nama_pelajaran, nama_guru))

        # Kembalikan nama kelas, jadwal, dan None (tidak ada error)
        return nama_kelas, jadwal, None

    except sqlite3.Error as e:
        return None, [], f"Error saat mengakses database: {e}"

    finally:
        if conn:
            conn.close()

def absensi(page_title):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        mata_pelajaran = []

        # Ambil daftar mata pelajaran untuk dropdown
        cursor.execute("SELECT id_mapel, nama_pelajaran FROM mapel")
        mata_pelajaran = cursor.fetchall()

        nis = session.get('nis')

        if not nis:
            return redirect(url_for('login')) 

        if request.method == 'POST':
            id_mapel = request.form['mapel']  # Menggunakan id_mapel yang dipilih dari dropdown
            action = request.form['action']
            qr_code = request.form['qr_code']
            

            # Ambil nama pelajaran berdasarkan id_mapel
            cursor.execute("SELECT nama_pelajaran FROM mapel WHERE id_mapel = ?", (id_mapel,))
            nama_pelajaran = cursor.fetchone()[0]

            # Verifikasi QR code dari tabel generate
            cursor.execute("SELECT COUNT(*) FROM generate WHERE matapelajaran = ? AND qr_code = ?", (nama_pelajaran, qr_code))
            qr_valid = cursor.fetchone()[0]

            if qr_valid == 0:
                print(f"Nama Pelajaran: {nama_pelajaran}, QR Code: {qr_code}")
                return "QR code tidak valid.", 400
                

            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if action == 'checkin':
                cursor.execute("INSERT INTO kehadiran (NIS, id_mapel, checkin) VALUES (?, ?, ?)", (nis, id_mapel, now))
            elif action == 'checkout':
                cursor.execute("UPDATE kehadiran SET checkout = ? WHERE NIS = ? AND id_mapel = ? AND checkout IS NULL", (now, nis, id_mapel))
            else:
                return "Aksi tidak valid.", 400
            
            conn.commit()

    except sqlite3.Error as e:
        return f"Terjadi kesalahan pada database: {e}"
    
    finally:
        if conn:
            conn.close()

    return render_template('murid/absensi_siswa.html', mata_pelajaran=mata_pelajaran, page_title='Absensi Siswa')


def generate_code():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        qr_code_path = None  
        mata_pelajaran = []  


        cursor.execute("SELECT id_mapel, nama_pelajaran FROM mapel")
        mata_pelajaran = cursor.fetchall()

        if request.method == 'POST':
            nama_guru = session.get('nama_guru') 
            mapel_id = request.form.get('mapel')
            jam1 = request.form.get('jam1')
            jam2 = request.form.get('jam2')

            if not nama_guru or not mapel_id or not jam1 or not jam2:
                flash('Semua kolom harus diisi!', 'danger')
                return render_template('guru/generate_code.html', qr_code_path=None, mata_pelajaran=mata_pelajaran)

            cursor.execute("SELECT nama_pelajaran FROM mapel WHERE id_mapel = ?", (mapel_id,))
            nama_pelajaran_row = cursor.fetchone()

            if not nama_pelajaran_row:
                flash('Mata pelajaran tidak ditemukan!', 'danger')
                return render_template('guru/generate_code.html', qr_code_path=None, mata_pelajaran=mata_pelajaran)

            nama_pelajaran = nama_pelajaran_row[0]

            # Generate kode acak (gunakan fungsi generate_random_code())
            random_code = generate_random_code()

            # Data untuk QR Code (kode acak)
            qr_data = f"Random Code: {random_code}"

            # Generate QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            # Buat gambar QR Code
            img = qr.make_image(fill='black', back_color='white')

            # Simpan QR Code ke folder static
            qr_code_dir = 'static/qrcodes'
            qr_code_path = f'{qr_code_dir}/{random_code}_qr.png'
            
            # Buat folder jika belum ada
            if not os.path.exists(qr_code_dir):
                os.makedirs(qr_code_dir)

            # Simpan gambar QR code
            img.save(qr_code_path)

            cursor.execute("""
                INSERT INTO generate (id_guru, matapelajaran, jam_1, jam_2, qr_code)
                VALUES (?, ?, ?, ?, ?)
            """, (nama_guru, nama_pelajaran, jam1, jam2, random_code))
            conn.commit()

            flash('QR Code berhasil di-generate dan data berhasil disimpan!', 'success')

    except sqlite3.Error as e:
        flash(f"Terjadi kesalahan pada database: {e}", 'danger')
    
    finally:
        if conn:
            conn.close()

    return qr_code_path, mata_pelajaran
