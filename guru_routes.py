from flask import Blueprint, render_template, request, session, redirect, url_for
import Fungsi_CRUD

guru_bp = Blueprint('guru_bp', __name__)

@guru_bp.route('/halaman_guru')
def halaman_guru():
    if 'username' in session:
        return render_template('guru/tampilkan_guru.html', nama_guru=session['nama_guru'])
    else:
        return redirect(url_for('login'))

@guru_bp.route('/tampilkan_guru')
def tampilkan_guru():
    return Fungsi_CRUD.tampilkan_guru(page_title='Semua Guru')

@guru_bp.route('/generate_code', methods=['GET', 'POST'])
def generate_code():
    qr_code_path, mata_pelajaran = Fungsi_CRUD.generate_code()
    return render_template('guru/generate_code.html', qr_code_path=qr_code_path, mata_pelajaran=mata_pelajaran, page_title='Generate QR Code')
