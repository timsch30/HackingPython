# Einfache Webanwendung

## Start (lokaler PostgreSQL-Server)

```bash
cd simple_webapp
pip install flask flask-sqlalchemy psycopg[binary]
set DATABASE_URL=postgresql+psycopg://appuser:3215@localhost:5432/Local_Postgres_Hacking_Python_PW_3215
python app.py
```

Dann im Browser: `http://127.0.0.1:5000`

## Datenbank

Die Anwendung nutzt jetzt **Flask-SQLAlchemy** (im Stil `db = SQLAlchemy(app)`) und ist auf deinen lokalen PostgreSQL-Betrieb ausgelegt.

- Standard (falls `DATABASE_URL` nicht gesetzt):
  `postgresql+psycopg://appuser:3215@localhost:5432/Local_Postgres_Hacking_Python_PW_3215`
- Empfohlen: `DATABASE_URL` explizit setzen (siehe Start-Block oben).

## Enthaltene Seiten

- `/` Startseite mit Links zu Login und Registrierung
- `/register` Registrierung (Username + Passwort)
- `/login` Login (Cookie-basierte Authentifizierung)
- `/content` Geschützte Content-Seite
- `/detail/<id>` Detailseite mit Text aus Datenbank
- `/create` Formular zum Erstellen neuer Inhalte (mind. 1024 Zeichen)
- `/logout` Logout und Cookie-Löschung

## SQL-Injection-Check (für eigene Tests)

### Ergebnis für den aktuellen Stand

Die Login-Query in `app.py` ist absichtlich **unsicher** aufgebaut (String-Konkatenation per f-String) und damit für SQL-Injection-Übungen mit Burp geeignet. Die übrigen Datenbankzugriffe nutzen weiterhin gebundene Parameter.

### Empfohlene Vorgehensweise für deine Übung

1. Nur gegen eigene Instanz/Staging testen.
2. Testfälle gegen `/login`, `/register`, `/create` und URL-Parameter von `/detail/<id>` ausführen.
3. Auf unterschiedliche Antworten, SQL-Fehler und auffällige Response-Zeiten prüfen.
4. Ergebnisse dokumentieren (Request, erwartetes Verhalten, tatsächliches Verhalten, Risiko).

### Wichtige weitere Sicherheitsbaustellen (nicht SQLi)

- Passwörter werden aktuell im Klartext gespeichert. Empfohlen: gehashte Speicherung (z. B. `werkzeug.security.generate_password_hash` / `check_password_hash`).
- Login nutzt ein frei setzbares Cookie `name` für die Identität. Empfohlen: serverseitige Session mit signiertem Session-Cookie.

> Hinweis: Diese Übungsänderung ist absichtlich unsicher und sollte nur lokal bzw. in isolierten Trainingsumgebungen verwendet werden.
