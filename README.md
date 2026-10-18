# Data Engineering – Anbindung heterogener Datenquellen 🔌
Extraktion von Daten aus drei unterschiedlichen Quellsystemen mit Python

Dieses Studentenprojekt verbindet sich mit drei Datenquellen (Shop, Energie, Wetter), die jeweils auf einem anderen Datenbanksystem laufen und zusätzlich eine REST-API bereitstellen. Die Daten werden mit pandas als DataFrames geladen und können so weiterverarbeitet werden.

*Hinweis: Die Zugangsdaten zu den Quellsystemen sind aus Good-Practice-Gründen nicht im Repository enthalten (siehe Setup) obwohl es sich hierbei lediglich um synthetische Daten handelt*

## 🛠 Tools & Daten
* **Programmiersprache:** Python (Paketverwaltung via `venv` + `requirements.txt`)
* **Verwendete Kernpakete:** `python-dotenv`, `pandas`, `SQLAlchemy`, `requests`
* **Verwendete Datenbanktreiber:** `psycopg` (PostgreSQL), `PyMySQL` (MySQL), `pymongo` (MongoDB)
* **Daten (Grobe Übersicht):** Shop-, Energie- und Wetterdaten, abgefragt direkt aus den jeweiligen Datenbanken sowie über die Status-Endpunkte der APIs.

## 🚀 Setup & Ausführung

1. **Abhängigkeiten installieren**
   ```bash
   cd **PROJEKTPFAD**
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Zugangsdaten hinterlegen**
   Im Projekt-Root muss eine `.env`-Datei angelegt werden. Diese wird nicht versioniert. Als Vorlage dient `.env.example`, die alle benötigten Variablen enthält:
   ```bash
   cp .env.example .env
   ```
   Anschliessend die Werte in der `.env` mit den Zugangsdaten zu den Quellsystemen ergänzen.

3. **Projekt ausführen**
   ```bash
   python main.py
   ```
   Dies prüft für jede Quelle den API-Status (`/api/status`) und lädt anschliessend die Daten aus der jeweiligen Datenbank.

## 📁 Projektstruktur

| Pfad | Inhalt |
| --- | --- |
| `main.py` | **Hauptskript:** ruft alle drei Datenquellen nacheinander auf. |
| `shop.py` | Anbindung an die Shop-Datenbank (PostgreSQL) und deren API. |
| `energy.py` | Anbindung an die Energie-Datenbank (MySQL) und deren API. |
| `weather.py` | Anbindung an die Wetter-Datenbank (MongoDB) und deren API. |
| `requirements.txt` | Liste der benötigten Python-Pakete mit fixen Versionen. |
| `.env.example` | Vorlage mit allen benötigten Umgebungsvariablen (ohne Werte). |
| `.env` | *Lokal:* Zugangsdaten zu den Quellsystemen. -> Muss am Anfang manuell erstellt werden (siehe Setup). |

## 🔌 Datenquellen

| Quelle | Datenbank | Haupttabelle | Bemerkung |
| --- | --- | --- | --- |
| Shop | PostgreSQL | `orders` | Verknüpfung mit `order_items`, `products` und `customers` |
| Energie | MySQL | `readings` | Verknüpfung mit `meters`, inkrementelles Laden über `change_seq` |
| Wetter | MongoDB | – | Aktuell werden die vorhandenen Collections aufgelistet |
