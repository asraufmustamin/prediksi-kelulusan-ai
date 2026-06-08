from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

import pandas as pd
import numpy as np
import os
import joblib
import sqlite3

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix

try:
    model = joblib.load('model_kelulusan.pkl')
except FileNotFoundError:
    model = None

app = Flask(__name__)

app.secret_key = "secret123"

UPLOAD_FOLDER = 'dataset'

ALLOWED_EXTENSIONS = {'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# =========================
# LOGIN USER
# =========================

users = {
    "admin": "admin123",
    "operator": "operator123"
}

# =========================
# VALIDASI FILE
# =========================

def allowed_file(filename):

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =========================
# DATABASE SQLITE
# =========================

DB_PATH = "database.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

# =========================
# BUAT DATASET JIKA BELUM ADA
# =========================

def init_db():
    try:
        df_check = pd.read_sql("SELECT * FROM mahasiswa", conn)
        return df_check
    except:
        # Jika tabel belum ada, buat data dummy
        dummy = pd.DataFrame({
            'NIM': ['22001', '22002', '22003'],
            'Nama': ['Andi', 'Budi', 'Citra'],
            'IPK': [3.5, 2.7, 3.8],
            'Kehadiran': [90, 65, 95],
            'SKS_Lulus': [120, 90, 140],
            'Jenis_Kelamin': [1, 1, 0],
            'Matkul_Diulang': [0, 2, 0],
            'Semester': [6, 6, 6],
            'Lulus': [1, 0, 1]
        })
        dummy.to_sql('mahasiswa', conn, if_exists='replace', index=False)
        return dummy

df = init_db()

# =========================
# FUNCTION TRAINING MODEL
# =========================

def training_model(dataframe):

    X = dataframe[['IPK', 'Kehadiran', 'SKS_Lulus', 'Jenis_Kelamin', 'Matkul_Diulang', 'Semester']]

    y = dataframe['Lulus']

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled,
        y,
        test_size=0.2,
        random_state=42
    )

    model = RandomForestClassifier(random_state=42)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])

    return model, scaler, accuracy, cm

# =========================
# TRAINING PERTAMA
# =========================

model, scaler, accuracy, cm = training_model(df)

# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        if username in users and users[username] == password:

            session['user'] = username

            return redirect(url_for('dashboard'))

        else:

            error = "Username atau Password Salah"

    return render_template('login.html', error=error)

# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect(url_for('login'))

# =========================
# SETTINGS / GANTI PASSWORD
# =========================

@app.route('/settings', methods=['GET', 'POST'])
def settings():

    if 'user' not in session:

        return redirect(url_for('login'))

    pesan = None
    error = None

    if request.method == 'POST':

        username = session['user']

        password_lama = request.form['password_lama']

        password_baru = request.form['password_baru']

        konfirmasi = request.form['konfirmasi']

        # VALIDASI PASSWORD LAMA
        if users[username] != password_lama:

            error = "Password lama salah"

        # VALIDASI KONFIRMASI
        elif password_baru != konfirmasi:

            error = "Konfirmasi password tidak cocok"

        else:

            # UPDATE PASSWORD
            users[username] = password_baru

            pesan = "Password berhasil diganti"

    return render_template(
        'settings.html',
        pesan=pesan,
        error=error
    )

# =========================
# HAPUS DATA
# =========================

@app.route('/delete/<nim>')
def delete_data(nim):
    global df
    global model, scaler, accuracy, cm
    if 'user' not in session:
        return redirect(url_for('login'))
    
    df = df[df['NIM'].astype(str) != str(nim)]
    df.to_sql('mahasiswa', conn, if_exists='replace', index=False)
    
    try:
        model, scaler, accuracy, cm = training_model(df)
    except:
        pass
        
    return redirect(url_for('dashboard'))

@app.route('/delete_all', methods=['POST'])
def delete_all():
    global df
    global model, scaler, accuracy, cm
    if 'user' not in session:
        return redirect(url_for('login'))
    
    df = pd.DataFrame(columns=['NIM', 'Nama', 'IPK', 'Kehadiran', 'SKS_Lulus', 'Jenis_Kelamin', 'Matkul_Diulang', 'Semester', 'Lulus'])
    df.to_sql('mahasiswa', conn, if_exists='replace', index=False)
    
    cm = np.array([[0, 0], [0, 0]])
    accuracy = 0
    
    return redirect(url_for('dashboard'))

# =========================
# DASHBOARD
# =========================

@app.route('/', methods=['GET', 'POST'])
def dashboard():

    global df
    global model
    global scaler
    global accuracy
    global cm

    if 'user' not in session:

        return redirect(url_for('login'))

    # =========================
    # UPLOAD EXCEL
    # =========================

    if request.method == 'POST':

        if 'file' not in request.files:

            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':

            return redirect(request.url)

        if file and allowed_file(file.filename):

            # Upload file baru (Excel) dan replace SQLite
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'temp.xlsx'))
            df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], 'temp.xlsx'))
            df.to_sql('mahasiswa', conn, if_exists='replace', index=False)

            model, scaler, accuracy, cm = training_model(df)

    total_mahasiswa = len(df)

    total_lulus = int(df['Lulus'].sum()) if total_mahasiswa > 0 else 0

    total_tidak = total_mahasiswa - total_lulus

    rata_prob = round(
        (total_lulus / total_mahasiswa) * 100 if total_mahasiswa > 0 else 0,
        2
    )

    return render_template(

        'dashboard.html',

        total_mahasiswa=total_mahasiswa,

        total_lulus=total_lulus,

        total_tidak=total_tidak,

        rata_prob=rata_prob,

        accuracy=round(accuracy * 100, 2),

        cm=cm.tolist(),

        data=df.to_dict(orient='records')

    )

# =========================
# PREDIKSI INDIVIDU
# =========================

@app.route('/prediksi', methods=['GET', 'POST'])
def prediksi():

    global df
    global model
    global scaler
    global accuracy
    global cm

    if 'user' not in session:

        return redirect(url_for('login'))

    hasil = None

    if request.method == 'POST':

        nim = request.form['nim']

        nama = request.form['nama']

        ipk = float(request.form['ipk'])

        kehadiran = float(request.form['kehadiran'])

        sks = float(request.form['sks'])

        jenis_kelamin = int(request.form['jenis_kelamin'])

        matkul_ulang = int(request.form['matkul_ulang'])

        semester = int(request.form['semester'])

        # =========================
        # PREDIKSI
        # =========================

        data = scaler.transform([
            [ipk, kehadiran, sks, jenis_kelamin, matkul_ulang, semester]
        ])

        pred = model.predict(data)[0]

        prob = model.predict_proba(data)[0][1]

        status = "Tepat Waktu" if pred == 1 else "Tidak Tepat Waktu"

        hasil = {
            'status': status,
            'probabilitas': round(prob * 100, 2)
        }

        # =========================
        # SIMPAN DATA BARU
        # =========================

        baru = pd.DataFrame({

            'NIM': [nim],

            'Nama': [nama],

            'IPK': [ipk],

            'Kehadiran': [kehadiran],

            'SKS_Lulus': [sks],

            'Jenis_Kelamin': [jenis_kelamin],

            'Matkul_Diulang': [matkul_ulang],

            'Semester': [semester],

            'Lulus': [1 if pred == 1 else 0]

        })

        df = pd.concat([df, baru], ignore_index=True)

        # =========================
        # UPDATE SQLITE
        # =========================

        df.to_sql('mahasiswa', conn, if_exists='replace', index=False)

        # =========================
        # TRAINING ULANG MODEL
        # =========================

        model, scaler, accuracy, cm = training_model(df)

    return render_template(
        'prediksi.html',
        hasil=hasil
    )

# =========================
# HAPUS DATA
# =========================

@app.route('/hapus/<int:index>')
def hapus(index):

    global df
    global model
    global scaler
    global accuracy
    global cm

    if 'user' not in session:

        return redirect(url_for('login'))

    df = df.drop(index)

    df = df.reset_index(drop=True)

    # UPDATE SQLITE
    df.to_sql('mahasiswa', conn, if_exists='replace', index=False)

    # TRAINING ULANG
    model, scaler, accuracy, cm = training_model(df)

    return redirect(url_for('dashboard'))

# =========================
# RUN APP
# =========================

if __name__ == '__main__':

    app.run(debug=True)