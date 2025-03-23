import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler



# Ordner für Uploads
UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------------------------
# 🎨 TITEL UND EINLEITUNG
# -----------------------------------
st.set_page_config(page_title="FinSight – Intelligente Bankanalysen", layout="centered")

# -----------------------------------
# 🎨 SIDEBAR DESIGN
# -----------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Bank_icon.svg/1200px-Bank_icon.svg.png", width=80)
    st.markdown("## 🏦 FinSight")
    st.markdown("**Die smarte Analyseplattform für Banken.**\n\n"
                "Analysieren Sie Ihre Kundendaten, entdecken Sie Muster, "
                "und gewinnen Sie Erkenntnisse mit nur wenigen Klicks.")
    st.markdown("---")
    st.markdown("### 🔍 <span style='color:#0455A4;'>Analyse auswählen</span>", unsafe_allow_html=True)

    st.markdown("👤 **Benutzer:** Demo-Modus")
    st.markdown("🕒 **Version:** 0.1 Beta")
    st.markdown("📬 support@finsight.ai")


st.markdown("<h1 style='color:#0455A4;'>📊 FinSight</h1>", unsafe_allow_html=True)
st.subheader("Intelligente Bankanalysen auf Knopfdruck")

st.markdown("Willkommen bei **FinSight**, Ihrer Analyseplattform für moderne Banken. "
            "Laden Sie Ihre Daten hoch und starten Sie sofort mit spannenden Auswertungen.")

st.markdown("---")

# -----------------------------------
# 📤 DATENUPLOAD
# -----------------------------------
st.markdown("### 📁 <span style='color:#0455A4;'>Daten-Upload</span>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Bitte laden Sie alle notwendigen CSV-Dateien hoch (z. B. Kunden, Transaktionen, Produkte, usw.).",
    accept_multiple_files=True,
    type=["csv"]
)

hochgeladene_dateien = []

if uploaded_files:
    for file in uploaded_files:
        file_path = os.path.join(UPLOAD_FOLDER, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        hochgeladene_dateien.append(file.name)

    st.success("✅ Alle Daten sind vollständig hochgeladen.")
    st.markdown("Folgende Dateien wurden gespeichert:")
    for name in hochgeladene_dateien:
        st.markdown(f"📄 {name}")

    st.markdown("---")
    
    # -----------------------------------
    # 📊 ANALYSEMÖGLICHKEITEN
    # -----------------------------------
    st.header("🔍 Analyse auswählen")

    analysen = {
        "📂 Vorliegende Daten analysieren": [
            "Kundensegmente erkennen",
            "Produktverteilung anzeigen",
            "Transaktionsvolumen nach Kanal",
            "Durchschnittliche Kontobewegungen",
            "Alter vs. Produkttyp"
        ],
        "🔮 Zukünftige Analysen & Muster": [
            "Churn Prediction",
            "Kreditwürdigkeitsschätzung",
            "Produktverteilung anzeigen",
            "Clusteranalyse von Transaktionen",
            "Saisonale Mustererkennung"
        ],
        "💬 Customer Sentiment & Verhalten": [
            "Analyse von Sessionverhalten",
            "Churn-Wahrscheinlichkeit aus Cookie-Daten"
        ]
    }

    kategorie = st.selectbox("Kategorie auswählen", list(analysen.keys()))
    option = st.selectbox("Analyseoption auswählen", analysen[kategorie])
if st.button("🚀 Analyse starten", key="analyse_button"):

    if st.button("🚀 Analyse starten"):

     if option == "Kundensegmente erkennen":
        try:
            # 📥 CSV-Dateien laden
            df_kunden = pd.read_csv(os.path.join(UPLOAD_FOLDER, "KUNDEN.csv"))
            df_produkte = pd.read_csv(os.path.join(UPLOAD_FOLDER, "BANK_PRODUKTE.csv"))

            # 📆 Alter berechnen
            df_kunden['Geburtsdatum'] = pd.to_datetime(df_kunden['Geburtsdatum'])
            df_kunden['Alter'] = (pd.Timestamp('today') - df_kunden['Geburtsdatum']).dt.days // 365

            # 🎯 Produktanzahl je Kunde berechnen
            produktanzahl = df_produkte.groupby("Kundennummer").size().reset_index(name="Produktanzahl")

            # 🔗 Mergen & Aufbereiten
            df_merged = pd.merge(df_kunden, produktanzahl, on="Kundennummer", how="left")
            df_merged['Geschlecht'] = df_merged['Geschlecht'].map({'Mann': 0, 'Frau': 1, 'Divers': 2})
            df_merged['Bildung'] = df_merged['Bildung'].map({
                'kein Schulabschluss': 0,
                'Lehre': 1,
                'Matura': 2,
                'Studium': 3
            })

            # 🧠 Clustering mit KMeans
            features = df_merged[['Alter', 'Geschlecht', 'Bildung', 'Produktanzahl']]
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(features)

            kmeans = KMeans(n_clusters=4, random_state=42)
            df_merged['Cluster'] = kmeans.fit_predict(X_scaled)

            st.success("✅ Kundensegmente erfolgreich erkannt!")

            # 📊 Cluster-Übersicht
            st.markdown("### 🔎 Übersicht über die Segmente")
            st.dataframe(df_merged.groupby('Cluster')[['Alter', 'Produktanzahl']].mean().round(1))

            # 📈 Visualisierung: Alter vs Produktanzahl
            fig, ax = plt.subplots()
            for cluster in sorted(df_merged['Cluster'].unique()):
                cluster_data = df_merged[df_merged['Cluster'] == cluster]
                ax.scatter(cluster_data['Alter'], cluster_data['Produktanzahl'], label=f"Cluster {cluster}", alpha=0.6)
            ax.set_xlabel("Alter")
            ax.set_ylabel("Anzahl Produkte")
            ax.set_title("Kundensegmente: Alter vs. Produktanzahl")
            ax.legend()
            st.pyplot(fig)

        except Exception as e:
            st.error(f"❌ Fehler bei der Analyse: {e}")

    elif option == "Durchschnittliche Kontobewegungen":
        try:
            df_transaktionen = pd.read_csv(os.path.join(UPLOAD_FOLDER, "TRANSAKTIONEN.csv"))

            # Datum formatieren
            df_transaktionen['Datum'] = pd.to_datetime(df_transaktionen['Datum'])

            # Monat extrahieren
            df_transaktionen['Monat'] = df_transaktionen['Datum'].dt.to_period('M')

            # Eingänge und Ausgänge trennen
            df_transaktionen['Eingang'] = df_transaktionen['Betrag'].apply(lambda x: x if x > 0 else 0)
            df_transaktionen['Ausgang'] = df_transaktionen['Betrag'].apply(lambda x: x if x < 0 else 0)

            # Gruppieren nach Kundennummer und Monat
            gruppiert = df_transaktionen.groupby(['Kundennummer', 'Monat']).agg({
                'Eingang': 'sum',
                'Ausgang': 'sum'
            }).reset_index()

            # Durchschnitt je Kunde berechnen
            df_avg = gruppiert.groupby('Kundennummer').agg({
                'Eingang': 'mean',
                'Ausgang': 'mean'
            }).reset_index()
            df_avg['Saldo'] = df_avg['Eingang'] + df_avg['Ausgang']

            st.success("✅ Analyse erfolgreich durchgeführt!")

            st.markdown("### 💰 Durchschnittliche Kontobewegungen pro Monat (je Kunde)")
            st.dataframe(df_avg.head(20).round(2))  # erste 20 Kunden

            # Visualisierung
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.hist(df_avg['Saldo'], bins=50, color='steelblue', alpha=0.7)
            ax.set_title("Verteilung der durchschnittlichen Monatssaldi")
            ax.set_xlabel("Saldo (€)")
            ax.set_ylabel("Anzahl Kunden")
            st.pyplot(fig)

        except Exception as e:
            st.error(f"❌ Fehler bei der Analyse: {e}")

    elif option == "Produktverteilung anzeigen":
        try:
            df_produkte = pd.read_csv(os.path.join(UPLOAD_FOLDER, "BANK_PRODUKTE.csv"))

            # Produktanzahl berechnen
            produkt_counts = df_produkte['Produktname'].value_counts().reset_index()
            produkt_counts.columns = ['Produktname', 'Anzahl']
            produkt_counts['Anteil (%)'] = (produkt_counts['Anzahl'] / produkt_counts['Anzahl'].sum() * 100).round(2)

            st.success("✅ Produktverteilung erfolgreich analysiert!")
            st.markdown("### 📦 Verteilung der Bankprodukte")
            st.dataframe(produkt_counts)

            # 📊 Visualisierung
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.bar(produkt_counts['Produktname'], produkt_counts['Anzahl'], color="#0455A4")
            ax.set_title("Häufigkeit der Bankprodukte")
            ax.set_ylabel("Anzahl")
            ax.set_xticklabels(produkt_counts['Produktname'], rotation=45, ha='right')
            st.pyplot(fig)

        except Exception as e:
            st.error(f"❌ Fehler bei der Analyse: {e}")

    elif option == "Churn-Wahrscheinlichkeit aus Cookie-Daten":
        try:
            df_cookie = pd.read_csv(os.path.join(UPLOAD_FOLDER, "COOKIE_DATEN.csv"))

            st.success("✅ Kundensentiment erfolgreich analysiert!")

            st.markdown("### 💬 Churn & Nutzerverhalten")

            # Grundübersicht
            avg_churn = df_cookie['Churn-Wahrscheinlichkeit'].mean()
            st.metric(label="📉 Durchschnittliche Churn-Wahrscheinlichkeit", value=f"{avg_churn:.2%}")

            # Abbruchrate
            abbruchrate = df_cookie['Abbruch'].mean()
            st.metric(label="❌ Abbruchrate (über alle Sessions)", value=f"{abbruchrate:.2%}")

            # Sessiondauer & Seitenaufrufe – Boxplot
            import seaborn as sns
            import matplotlib.pyplot as plt

            fig1, ax1 = plt.subplots()
            sns.histplot(df_cookie['Sessiondauer (Sekunden)'], kde=True, ax=ax1, color="skyblue")
            ax1.set_title("⏱️ Verteilung der Sessiondauer")
            ax1.set_xlabel("Sessiondauer (Sekunden)")
            st.pyplot(fig1)

            # Top-Interessen
            st.markdown("### 🔍 Häufigste Interessen")
            st.bar_chart(df_cookie['Top-Interesse'].value_counts())

        except Exception as e:
            st.error(f"❌ Fehler bei der Analyse: {e}")


    else:
        st.info(f"Analyse **{option}** wurde gestartet... (folgt später)")
