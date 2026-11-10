# AMATEGEKO Y'UMUHANDA – Rwanda Driving Licence Examination System

Urubuga rwa mbere mu Rwanda rwo kwiga amategeko y'umuhanda no kwitegura neza ikizamini cy'uruhushya rw'agateganyo (Provisional Driving License) gitangirwa kuri **Polisi y'u Rwanda / Irembo**.

---

## 🌟 Iby'Ingenzi Bigize Sisitemu (Key Features)

1. **Ikizamini cya Leta cy'Icyitegererezo (Official Mock Exam - 20/20)**
   - Ibibazo 20 bitoranywa mu buryo bwa mudasobwa (random selection).
   - Iminota 20 ibarwa ku isaha (20-minute countdown timer).
   - Ikizamini cyikora cyonyine iyo igihe kirangiye.
   - Amanota yo gutsinda ni **12/20 (60%)** - **WATSINZE** cyangwa **WATSINZWE**.
   - Gusubiramo amakosa (Review mistakes) n'ibisobanuro bishingiye ku *Iteka rya Perezida N° 85/01*.

2. **Kuvanga Ibyapa n'Amagambo (Balanced Mix of Signs & Words)**
   - Hafi 45% (ibibazo 9 kuri 20) by'amashusho y'ibyapa n'imiterere y'umuhanda.
   - Hafi 55% (ibibazo 11 kuri 20) by'amategeko mu magambo y'Ikinyarwanda.

3. **Kora Ikizamini Cyawe (Make Custom Exam / Exam Builder)**
   - Hitamo icyiciro wifuza (Category filter).
   - Hitamo umubare w'ibibazo (10, 20, 30, cyangwa 50).
   - Hitamo igihe wifuza (10 min, 20 min, 30 min, 50 min).
   - Hitamo uburemere (Kworoshye, Kuringaniye, Gikomeye).

4. **Imyitozo n'Ijwi ryo Gusoma (Interactive Practice with Voice Reader)**
   - Kwimenyereza ikibazo ku kindi ufashijwe n'ijwi rya mudasobwa (Web Speech API).
   - Kubona igisubizo ako kanya (Instant feedback: Icyatsi / Umutuku).
   - Kubika ibibazo bikugoye (Bookmarking system).

5. **Isomero ry'Ibyapa byo mu Muhanda (Visual Road Signs Library)**
   - Ibyapa biburira (Warning), ibibuza (Prohibition), ibitegeka (Mandatory), ibimenyesha (Information), iby'icyerekezo (Direction), n'iby'agateganyo (Temporary).
   - Ishusho ya vector (SVG) isobanutse neza kuri buri cyapa.

6. **Icyemezo cyo Gutsinda (Printable Official Certificate)**
   - Icyemezo kiriho numero y'ikizamini (Serial No), amazina y'umunyeshuri, n'amanota yatsindiyeho.

7. **Dashboard y'Umunyeshuri n'iy'Umuyobozi (Student & Admin Dashboards)**
   - Imbonerahamwe y'amanota (Chart.js score progression).
   - Urutonde rw'ibizamini byakozwe n'ibyo watsinze.
   - Admin Portal yo kongeramo, guhindura no gusiba ibibazo n'ibyapa.

---

## 🛠️ Ikoranabuhanga Ryakoreshejwe (Tech Stack)

- **Backend**: Python 3.12, Django 5.1
- **Database**: SQLite3 (Development) / PostgreSQL-ready (Production)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.3, Font Awesome 6
- **Data Visualizations**: Chart.js
- **PDF Processing**: pypdf, Pillow

---

## 🚀 Uko Wayatsa ku Mashini Yawe (Installation & Setup)

```powershell
# 1. Kora clone ya repository
git clone https://github.com/claudeutuy57/AMATEGEKO.git
cd AMATEGEKO

# 2. Fungura virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Shyiramo ibyangombwa (Dependencies)
pip install -r requirements.txt

# 4. Kora migrations z'imbonerahamwe z'amakuru
python manage.py migrate

# 5. Injizamo ibyapa n'amasomo
python manage.py seed_data

# 6. Injizamo ibibazo bya Polisi y'u Rwanda
python manage.py import_official_questions

# 7. Tangiza seriveri
python manage.py runserver
```

Fungura browser kuri: **http://127.0.0.1:8000/**

---

## 🔑 Konti z'Icyitegererezo (Demo Accounts)

- **Admin (Umuyobozi)**: `admin` / `AdminPassword123!`
- **Umunyeshuri (Learner)**: `umunyeshuri` / `StudentPassword123!`

---

## ⚖️ Amategeko Agenga Uru Rugendo
Biteguwe hashingiwe ku **Iteka rya Perezida N° 85/01 ryo ku wa 02/09/2002** rigenga amategeko rusange y'umuhanda n'ubugenzuzi bwo kugenda mu muhanda muri Repubulika y'u Rwanda.
