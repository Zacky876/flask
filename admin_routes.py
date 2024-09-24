from flask import Blueprint, render_template, request, session, redirect, url_for
import Fungsi_CRUD

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/halaman_admin')
def halaman_admin():
    if 'username' in session:
        return render_template('admin/halaman_admin.html', username=session['username'], page_title='Dashboard')
    else:
        return redirect(url_for('login'))

@admin_bp.route('/tambah_siswa', methods=['GET', 'POST'])
def tambah_siswa():
    return Fungsi_CRUD.tambah_siswa(page_title='Tambah Siswa')

@admin_bp.route('/hapus_siswa', methods=['GET', 'POST'])
def hapus_siswa():
    return Fungsi_CRUD.hapus_siswa(page_title='Hapus Siswa')

@admin_bp.route('/update_siswa', methods=['GET', 'POST'])
def update_siswa():
    return Fungsi_CRUD.update_siswa(page_title='Update Siswa')

@admin_bp.route('/tambah_guru', methods=['GET', 'POST'])
def tambah_guru():
    return Fungsi_CRUD.tambah_guru(page_title='Tambah Guru')

@admin_bp.route('/hapus_guru', methods=['GET', 'POST'])
def hapus_guru():
    return Fungsi_CRUD.hapus_guru(page_title='Hapus Guru')

@admin_bp.route('/update_guru', methods=['GET', 'POST'])
def update_guru():
    return Fungsi_CRUD.update_guru(page_title='Update Guru')

@admin_bp.route('/tampilkan_data', methods=['GET', 'POST'])
def tampilkan_data():
    if request.method == 'POST':
        tahun = request.form['tahun']
        return Fungsi_CRUD.Tampilkan_data(tahun)
    return render_template('tampilkan_pertahun.html', page_title='Data Siswa Pertahun')
    
@admin_bp.route('/tampilkan_perhari', methods=['GET', 'POST'])
def tampilkan_jadwal_view():
    if request.method == 'POST':
        siswa = request.form['siswa']
        return Fungsi_CRUD.tampilkan_jadwal(siswa)
    return render_template('tampilkan_perhari.html', page_title='Jadwal Siswa Perhari')

@admin_bp.route('/jumlah_jam_mapel', methods=['GET', 'POST'])
def jumlah_jam_mapel_view():
    if request.method == 'POST':
        bulan = request.form['bulan']  # Mengambil data 'bulan' dari form
        jenis_kelamin = request.form['jenis_kelamin']  # Mengambil data 'jenis_kelamin' dari form
        pelajaran = request.form['pelajaran']  # Mengambil data 'pelajaran' dari form
        return Fungsi_CRUD.jumlah_jam_mapel(bulan, jenis_kelamin, pelajaran)
    return render_template('tampilkan_jam_mapel.html', page_title='Jumlah Jam Mapel')