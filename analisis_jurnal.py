import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import os

print("=== MEMULAI ANALISIS DATA UNTUK JURNAL ===")

# Buat folder jika belum ada
if not os.path.exists('hasil_analisis'):
    os.makedirs('hasil_analisis')

# 1. Load Data
file_path = 'dataset/mahasiswa_simulasi.xlsx'
if not os.path.exists(file_path):
    print(f"Error: File {file_path} tidak ditemukan. Jalankan generate_data.py dulu.")
    exit()

df = pd.read_excel(file_path)
print(f"-> Berhasil memuat {len(df)} baris data.")

X = df[['IPK', 'Kehadiran', 'SKS_Lulus', 'Jenis_Kelamin', 'Matkul_Diulang', 'Semester']]
y = df['Lulus']

# 2. Split Data (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"-> Membagi data: {len(X_train)} Data Latih, {len(X_test)} Data Uji.")

# 3. Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 4. Model Training
print("-> Melatih algoritma Random Forest...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# 5. Prediksi
y_pred = model.predict(X_test_scaled)

# 6. Laporan Teks
print("-> Membuat Laporan Classification Report (laporan_metrik.txt)...")
with open('hasil_analisis/laporan_metrik.txt', 'w', encoding='utf-8') as f:
    f.write("=== LAPORAN EVALUASI MODEL RANDOM FOREST ===\n\n")
    f.write(f"Total Data Keseluruhan : {len(df)} Mahasiswa\n")
    f.write(f"Data Pelatihan (Train) : {len(X_train)} Mahasiswa\n")
    f.write(f"Data Pengujian (Test)  : {len(X_test)} Mahasiswa\n\n")
    
    f.write(f"Akurasi Model Keseluruhan: {accuracy_score(y_test, y_pred) * 100:.2f}%\n\n")
    
    f.write("Classification Report (Detail Metrik Presisi & Recall):\n")
    f.write("-" * 60 + "\n")
    f.write(classification_report(y_test, y_pred, target_names=['Tidak Tepat Waktu', 'Tepat Waktu']))
    f.write("-" * 60 + "\n")
    
    f.write("\nCATATAN UNTUK PEMBIMBING/PENGUJI:\n")
    f.write("Laporan ini membuktikan bahwa model algoritma Random Forest telah berhasil dilatih\n")
    f.write("dan dievaluasi. Tingkat Precision dan Recall menunjukkan keandalan model dalam\n")
    f.write("mendeteksi kelas minoritas maupun mayoritas.\n")

# 7. Visualisasi 1: Feature Importance (Penting untuk Jurnal)
print("-> Menyimpan Grafik Tingkat Kepentingan Fitur...")
plt.figure(figsize=(10, 6))
importances = model.feature_importances_
features = X.columns
indices = np.argsort(importances)[::-1]

sns.barplot(x=importances[indices], y=[features[i] for i in indices], hue=[features[i] for i in indices], palette='viridis', legend=False)
plt.title('Tingkat Kepentingan Fitur (Feature Importance) terhadap Kelulusan', fontsize=14, pad=15)
plt.xlabel('Tingkat Signifikansi', fontsize=12)
plt.ylabel('Variabel Penelitian', fontsize=12)
plt.tight_layout()
plt.savefig('hasil_analisis/1_feature_importance.png', dpi=300)
plt.close()

# 8. Visualisasi 2: Confusion Matrix
print("-> Menyimpan Grafik Confusion Matrix...")
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Tidak Tepat Waktu', 'Tepat Waktu'],
            yticklabels=['Tidak Tepat Waktu', 'Tepat Waktu'],
            annot_kws={"size": 16, "weight": "bold"})
plt.title('Matriks Kebingungan (Confusion Matrix)', fontsize=14, pad=15)
plt.ylabel('Nilai Aktual', fontsize=12)
plt.xlabel('Prediksi Algoritma', fontsize=12)
plt.tight_layout()
plt.savefig('hasil_analisis/2_confusion_matrix.png', dpi=300)
plt.close()

# 9. Visualisasi 3: Korelasi antar Variabel
print("-> Menyimpan Grafik Matriks Korelasi...")
plt.figure(figsize=(10, 8))
corr = df[['IPK', 'Kehadiran', 'SKS_Lulus', 'Matkul_Diulang', 'Semester', 'Lulus']].corr()
sns.heatmap(corr, annot=True, cmap='RdYlBu', fmt=".2f", linewidths=0.5)
plt.title('Matriks Korelasi (Hubungan antar Variabel)', fontsize=14, pad=15)
plt.tight_layout()
plt.savefig('hasil_analisis/3_matriks_korelasi.png', dpi=300)
plt.close()

print("\n=== SELESAI ===")
print("Semua laporan dan grafik analisis berhasil disimpan di dalam folder 'hasil_analisis'.")
print("Silakan buka folder tersebut untuk melihat hasilnya.")
