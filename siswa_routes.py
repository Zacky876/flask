from flask import Blueprint, render_template, request, session, redirect, url_for
import Fungsi_CRUD

murid_bp = Blueprint('murid_bp', __name__)

@murid_bp.route('/halaman_siswa')
def halaman_siswa():
    if 'username' in session:
        return redirect(url_for('murid_bp.tampilkan_siswa', nama_siswa=session['nama_siswa']))
    else:
        return redirect(url_for('login'))

@murid_bp.route('/tampilkan_siswa')
def tampilkan_siswa(): 
    return Fungsi_CRUD.tampilkan_siswa(page_title='Semua Siswa')

@murid_bp.route('/absensi_siswa', methods=['GET', 'POST'])
def absensi_siswa():
    return Fungsi_CRUD.absensi(page_title='Absensi Siswa')
    
@murid_bp.route('/tampilkan_jadwal')
def tampilkan_jadwal():
    return Fungsi_CRUD.tampilkan_jadwal_siswa(page_title='Semua Jadwal Siswa')