# Data Engineering – Anbindung heterogener Datenquellen 🔌
Extraktion von Daten aus drei unterschiedlichen Quellsystemen mit Python und Laden in ein lokales Data Warehouse

Dieses Studentenprojekt verbindet sich mit drei Datenquellen (Shop, Energie, Wetter), die jeweils auf einem anderen Datenbanksystem laufen und zusätzlich eine REST-API bereitstellen. Die Daten werden mit pandas als DataFrames geladen und in ein lokales PostgreSQL-Warehouse (Schema `raw`) geschrieben.

*Hinweis: Die Zugangsdaten zu den Quellsystemen sind aus Good-Practice-Gründen nicht im Repository enthalten (siehe Setup) obwohl es sich hierbei lediglich um synthetische Daten handelt*

## 🛠 Tools & Daten
* **Programmiersprache:** Python (Paketverwaltung via `venv` + `requirements.txt`)
* **Verwendete Kernpakete:** `python-dotenv`, `pandas`, `SQLAlchemy`, `requests`, `rich`
* **Verwendete Datenbanktreiber:** `psycopg` (PostgreSQL), `PyMySQL` (MySQL), `pymongo` (MongoDB)
* **Infrastruktur:** Docker / Docker Compose mit `postgres:17` als lokales Warehouse
* **Daten (Grobe Übersicht):** Shop-, Energie- und Wetterdaten, abgefragt direkt aus den jeweiligen Datenbanken sowie über die Status-Endpunkte (api/status) der Endpunkte.

## 🚀 Setup & Ausführung

1. **Abhängigkeiten installieren**
   ```bash
   cd **PROJEKTPFAD**
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Zugangsdaten hinterlegen**
   Im Projekt-Root muss eine `.env`-Datei angelegt werden. Diese wird nicht versioniert. Als Vorlage dient `.env.example`, die alle benötigten Variablen enthält (Quellsysteme und Warehouse):
   ```bash
   cp .env.example .env
   ```
   Anschliessend die Werte in der `.env` mit den Zugangsdaten zu den Quellsystemen ergänzen und die `DWH_*`-Werte für das lokale Warehouse frei wählen (z.B. `DWH_HOST=localhost`).

3. **Warehouse starten**
   ```bash
   cd **PROJEKTPFAD**
   docker compose up -d
   ```
   Docker Compose liest die `DWH_*`-Variablen aus der `.env`. Die SQL-Skripte in `sql/init/` legen Schemas und Ladestand-Tabellen an. Sie laufen nur beim ersten Start, solange das Volume `dwh_data` noch leer ist. Um das Warehouse komplett zurückzusetzen:
   ```bash
   docker compose down -v
   ```

4. **Projekt ausführen**
   ```bash
   python main.py
   ```
   Ablauf:
   * **Shop & Wetter:** API-Status (`/api/status`) abfragen und Daten aus der Quelldatenbank lesen (noch ohne Laden ins Warehouse).
   * **Energie:** `meters` wird vollständig nach `raw.energy_meters` geladen (ersetzt). `readings` wird inkrementell nach `raw.energy_readings` geladen, vom letzten Ladestand bis zum aktuellen `changeSeq` der API. Danach wird der Ladestand in `etl.load_state` nachgeführt.

## 📁 Projektstruktur

| Pfad | Inhalt |
| --- | --- |
| `main.py` | **Hauptskript:** richtet das Logging ein und ruft die Datenquellen sowie das Warehouse nacheinander auf. |
| `api.py` | Gemeinsame Abfrage der Status-Endpunkte (`/api/status`) inkl. `is_ready`-Prüfung. |
| `shop.py` | Anbindung an die Shop-Datenbank (PostgreSQL) und deren API. |
| `energy.py` | Anbindung an die Energie-Datenbank (MySQL): Voll- und inkrementelle Extraktion über `change_seq`. |
| `weather.py` | Anbindung an die Wetter-Datenbank (MongoDB) und deren API. |
| `warehouse.py` | Anbindung an das Warehouse: Ladestand lesen, Daten voll oder inkrementell nach `raw` schreiben. |
| `docker-compose.yml` | Lokales Warehouse (`postgres:17`) mit persistentem Volume. |
| `sql/init/01_schemas.sql` | Legt die Schemas `raw`, `staging`, `mart` und `etl` an. |
| `sql/init/02_load_state.sql` | Legt `etl.load_state` und `etl.load_runs` an, inkl. Startwert für `energy`/`readings`. |
| `requirements.txt` | Liste der benötigten Python-Pakete. |
| `.env.example` | Vorlage mit allen benötigten Umgebungsvariablen (ohne Zugangsdaten). |
| `.env` | *Lokal:* Zugangsdaten zu den Quellsystemen und zum Warehouse. -> Muss am Anfang manuell erstellt werden (siehe Setup). |

## 🔌 Datenquellen

| Quelle | Datenbank | Haupttabelle | Ziel im Warehouse | Bemerkung |
| --- | --- | --- | --- | --- |
| Shop | PostgreSQL | `orders` | – (noch nicht geladen) | Verknüpfung mit `order_items`, `products` und `customers` |
| Energie | MySQL | `readings` | `raw.energy_meters` (voll), `raw.energy_readings` (inkrementell) | Verknüpfung mit `meters`, inkrementelles Laden über `change_seq` |
| Wetter | MongoDB | – | – (noch nicht geladen) | Aktuell werden die vorhandenen Collections aufgelistet |

## 🏗 Warehouse & inkrementelles Laden

Das Warehouse ist in Schichten aufgeteilt:

| Schema | Zweck | Stand |
| --- | --- | --- |
| `raw` | Rohdaten, 1:1 aus den Quellen | befüllt (Energie) |
| `staging` | Bereinigte Daten | vorbereitet |
| `mart` | Auswertungsfertige Daten | vorbereitet |
| `etl` | Steuerung der Ladeläufe | `load_state` in Verwendung |

**Inkrementelles Laden (Wasserzeichen):**
1. Den letzten Ladestand `last_cursor` für Quelle und Tabelle aus `etl.load_state` lesen.
2. Den aktuellen `changeSeq` über die API der Quelle abfragen. Er dient als obere Grenze.
3. Alle Zeilen mit `last_cursor < change_seq <= changeSeq` aus der Quelle holen.
4. Die Zeilen an die `raw`-Tabelle anhängen und `last_cursor` auf `changeSeq` setzen, beides in einer Transaktion.

Die Tabelle `etl.load_runs` zur Protokollierung einzelner Ladeläufe ist bereits angelegt, wird aber noch nicht befüllt.
