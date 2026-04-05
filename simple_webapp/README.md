# Einfache Webanwendung

## Start

```bash
cd simple_webapp
pip install flask psycopg[binary]
set DATABASE_URL=postgresql://appuser:DeinStarkesPasswort@localhost:5432/appdb
python app.py
```

Dann im Browser: `http://127.0.0.1:5000`

## PostgreSQL statt SQLite

Die Anwendung verwendet jetzt PostgreSQL über `psycopg`.

- Standardmäßig nutzt die App die Umgebungsvariable `DATABASE_URL`.
- Falls `DATABASE_URL` nicht gesetzt ist, wird als Fallback diese lokale URL verwendet:
  `postgresql://appuser:DeinStarkesPasswort@localhost:5432/appdb`

## Enthaltene Seiten

- `/` Startseite mit Links zu Login und Registrierung
- `/register` Registrierung (Username + Passwort)
- `/login` Login (Cookie-basierte Authentifizierung)
- `/content` Geschützte Content-Seite
- `/detail/<id>` Detailseite mit Text aus Datenbank
- `/create` Formular zum Erstellen neuer Inhalte (mind. 1024 Zeichen)
- `/logout` Logout und Cookie-Löschung
