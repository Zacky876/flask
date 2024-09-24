from flask import Flask, session, redirect, render_template, url_for
from admin_routes import admin_bp
from guru_routes import guru_bp
from siswa_routes import murid_bp
import Fungsi_CRUD

app = Flask(__name__)

app.secret_key = "zangetsu888"
db_path = r"C:\Users\ASUS\OneDrive\Documents\PYTHON\LATIHAN PYTHON\akademik.db"

# Register Blueprint
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(guru_bp, url_prefix='/guru')
app.register_blueprint(murid_bp, url_prefix='/murid')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return Fungsi_CRUD.login()

@app.route('/')
def base():
    if 'username' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_bp.halaman_admin'))
        elif role == 'guru':
            return redirect(url_for('guru_bp.halaman_guru'))
        elif role == 'murid':
            return redirect(url_for('murid_bp.halaman_siswa'))
        else:
            # Jika role tidak sesuai, arahkan ke halaman login atau tampilkan error
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()  # Kosongkan seluruh session
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
