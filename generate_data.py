import pandas as pd
import numpy as np
import os

print("Memulai proses pembuatan data simulasi mahasiswa...")

# Pastikan folder dataset ada
if not os.path.exists('dataset'):
    os.makedirs('dataset')

np.random.seed(42)
n_samples = 350

# Features
# 1. Jenis Kelamin: 1 (Laki), 0 (Pr)
jenis_kelamin = np.random.choice([1, 0], size=n_samples, p=[0.45, 0.55])

# Kita tentukan dulu siapa yang lulus tepat waktu (70%) dan tidak (30%)
# Agar data masuk akal secara akademik
target = np.random.choice([1, 0], size=n_samples, p=[0.70, 0.30])

ipk = []
kehadiran = []
sks = []
matkul_ulang = []
semester = []

for t in target:
    if t == 1: # Tepat Waktu (Lulus)
        # Logika: Mahasiswa rajin
        ipk.append(round(np.random.uniform(3.0, 4.0), 2))
        kehadiran.append(int(np.random.uniform(85, 100)))
        sks.append(int(np.random.uniform(144, 150)))
        matkul_ulang.append(int(np.random.uniform(0, 1))) # Jarang ngulang
        semester.append(int(np.random.uniform(7, 8))) # Normal
    else: # Tidak Tepat Waktu (Terlambat)
        # Logika: Mahasiswa bermasalah / telat
        ipk.append(round(np.random.uniform(2.0, 3.1), 2))
        kehadiran.append(int(np.random.uniform(50, 85)))
        sks.append(int(np.random.uniform(110, 140)))
        matkul_ulang.append(int(np.random.uniform(2, 6))) # Sering ngulang
        semester.append(int(np.random.uniform(9, 14))) # Molor

# Generate NIM and Nama
nims = [f"2021{str(i).zfill(4)}" for i in range(1, n_samples+1)]
namas = [f"Mahasiswa Simulasi {i}" for i in range(1, n_samples+1)]

df = pd.DataFrame({
    'NIM': nims,
    'Nama': namas,
    'IPK': ipk,
    'Kehadiran': kehadiran,
    'SKS_Lulus': sks,
    'Jenis_Kelamin': jenis_kelamin,
    'Matkul_Diulang': matkul_ulang,
    'Semester': semester,
    'Lulus': target
})

# Save to excel
path_file = 'dataset/mahasiswa_simulasi.xlsx'
df.to_excel(path_file, index=False)
print(f"SUKSES: Data simulasi {n_samples} mahasiswa berhasil dibuat dan disimpan di {path_file}")
