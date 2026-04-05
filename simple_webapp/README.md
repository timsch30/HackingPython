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
