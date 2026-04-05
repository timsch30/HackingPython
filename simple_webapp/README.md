# Einfache Webanwendung

## Start

```bash
cd simple_webapp
python app.py
```

Dann im Browser: `http://127.0.0.1:5000`

## Enthaltene Seiten

- `/` Startseite mit Links zu Login und Registrierung
- `/register` Registrierung (Username + Passwort)
- `/login` Login (Cookie-basierte Authentifizierung)
- `/content` Geschützte Content-Seite
- `/detail/<id>` Detailseite mit Text aus Datenbank
- `/create` Formular zum Erstellen neuer Inhalte (mind. 1024 Zeichen)
- `/logout` Logout und Cookie-Löschung

Die Daten werden in `app.db` (SQLite) gespeichert.
