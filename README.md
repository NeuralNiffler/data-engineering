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
   * **Shop:** `customers` und `products` werden vollständig nach `raw.shop_*` geladen (ersetzt). `orders` wird inkrementell über `change_seq` geladen, `order_items` über das `change_seq`-Fenster der zugehörigen `orders`.
   * **Wetter:** `stations` (statische Stammdaten) wird vollständig nach `raw.weather_stations` geladen (ersetzt). `observations` wird inkrementell über `change_seq` nach `raw.weather_observations` geladen. `_id` wird weggelassen, verschachtelte Felder (`measurements.*`) werden zu Spalten wie `measurements_temperature_c` flachgeklopft.
   * **Energie:** `meters` wird vollständig nach `raw.energy_meters` geladen (ersetzt). `readings` wird inkrementell nach `raw.energy_readings` geladen, vom letzten Ladestand bis zum aktuellen `changeSeq` der API. Danach wird der Ladestand in `etl.load_state` nachgeführt.

## 🧪 Tests

Die Unit-Tests laufen ohne Zugangsdaten, Docker und Netzwerk:
```bash
pip install -r requirements-dev.txt
pytest -v
```

* **Umgebungsvariablen:** `tests/conftest.py` setzt Dummy-Werte, bevor die Module importiert werden. Die echte `.env` wird nicht verwendet.
* **Datenbanken:** Die Engines der Quellen Shop und Energie sowie des Warehouses werden pro Test durch eine SQLite-Datenbank im Arbeitsspeicher ersetzt. Für das Warehouse werden die Schemas `raw` und `etl` per `ATTACH` und die Funktion `now()` nachgebildet.
* **MongoDB:** Die Wetter-Datenbank wird durch `mongomock` im Arbeitsspeicher ersetzt.
* **APIs:** `requests.get` wird gemockt.

| Datei | Prüft |
| --- | --- |
| `tests/test_api.py` | Aufruf von `/api/status` (URL, Timeout), Auswertung von `ready`, Weitergabe von HTTP-Fehlern |
| `tests/test_energy.py` | Fenster der inkrementellen Extraktion (`cursor < change_seq <= upper_bound`) |
| `tests/test_shop.py` | Fenster der Child-Extraktion `order_items` über `orders.change_seq` |
| `tests/test_weather.py` | Fenster der inkrementellen Extraktion, Weglassen von `_id`, Flachklopfen von `measurements` |
| `tests/test_warehouse.py` | Inkrementelles Laden über zwei Läufe: Anhängen, Zählen des neuen Fensters, Nachführen von `last_cursor` |

`main.py` ist noch nicht durch Tests abgedeckt.

## 📁 Projektstruktur

| Pfad | Inhalt |
| --- | --- |
| `main.py` | **Hauptskript:** richtet das Logging ein und ruft die Datenquellen sowie das Warehouse nacheinander auf. |
| `api.py` | Gemeinsame Abfrage der Status-Endpunkte (`/api/status`) inkl. `is_ready`-Prüfung. |
| `shop.py` | Anbindung an die Shop-Datenbank (PostgreSQL) und deren API. |
| `energy.py` | Anbindung an die Energie-Datenbank (MySQL): Voll- und inkrementelle Extraktion über `change_seq`. |
| `weather.py` | Anbindung an die Wetter-Datenbank (MongoDB): Voll- und inkrementelle Extraktion über `change_seq`. |
| `warehouse.py` | Anbindung an das Warehouse: Ladestand lesen, Daten voll oder inkrementell nach `raw` schreiben. |
| `docker-compose.yml` | Lokales Warehouse (`postgres:17`) mit persistentem Volume. |
| `sql/init/01_schemas.sql` | Legt die Schemas `raw`, `staging`, `mart` und `etl` an. |
| `sql/init/02_load_state.sql` | Legt `etl.load_state` und `etl.load_runs` an, inkl. Startwerten für alle inkrementellen Tabellen. |
| `requirements.txt` | Liste der benötigten Python-Pakete. |
| `requirements-dev.txt` | Zusätzliche Pakete für die Entwicklung (`pytest`, `mongomock`). |
| `pytest.ini` | Konfiguration für pytest (Testordner `tests/`). |
| `tests/` | Unit-Tests für `api.py`, `energy.py`, `shop.py`, `weather.py` und `warehouse.py` (siehe Tests). |
| `.env.example` | Vorlage mit allen benötigten Umgebungsvariablen (ohne Zugangsdaten). |
| `.env` | *Lokal:* Zugangsdaten zu den Quellsystemen und zum Warehouse. -> Muss am Anfang manuell erstellt werden (siehe Setup). |

## 🔌 Datenquellen

| Quelle | Datenbank | Haupttabelle | Ziel im Warehouse | Bemerkung |
| --- | --- | --- | --- | --- |
| Shop | PostgreSQL | `orders` | `raw.shop_customers`, `raw.shop_products` (voll), `raw.shop_orders`, `raw.shop_order_items` (inkrementell) | `order_items` über `orders.change_seq` |
| Energie | MySQL | `readings` | `raw.energy_meters` (voll), `raw.energy_readings` (inkrementell) | Verknüpfung mit `meters`, inkrementelles Laden über `change_seq` |
| Wetter | MongoDB | `observations` | `raw.weather_stations` (voll), `raw.weather_observations` (inkrementell) | Verknüpfung mit `stations` über `station_id` |

## 🏗 Warehouse & inkrementelles Laden

Das Warehouse ist in Schichten aufgeteilt:

| Schema | Zweck | Stand |
| --- | --- | --- |
| `raw` | Rohdaten, 1:1 aus den Quellen | befüllt (Shop, Energie, Wetter) |
| `staging` | Bereinigte Daten | vorbereitet |
| `mart` | Auswertungsfertige Daten | vorbereitet |
| `etl` | Steuerung der Ladeläufe | `load_state` in Verwendung |

**Inkrementelles Laden (Wasserzeichen):**
1. Den letzten Ladestand `last_cursor` für Quelle und Tabelle aus `etl.load_state` lesen.
2. Den aktuellen `changeSeq` über die API der Quelle abfragen. Er dient als obere Grenze.
3. Alle Zeilen mit `last_cursor < change_seq <= changeSeq` aus der Quelle holen.
4. Die Zeilen an die `raw`-Tabelle anhängen und `last_cursor` auf `changeSeq` setzen, beides in einer Transaktion.

Die Tabelle `etl.load_runs` zur Protokollierung einzelner Ladeläufe ist bereits angelegt, wird aber noch nicht befüllt.
