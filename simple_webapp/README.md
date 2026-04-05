# Einfache Webanwendung

## Start

```bash
cd simple_webapp
python app.py
```

Dann im Browser: `http://127.0.0.1:5000`

## Enthaltene Seiten (laut Aufgabenstellung)

- `/` Entry Page mit Links zu Login und Register
- `/register` Register Page (Username + Password wird gespeichert)
- `/login` Login Page (Username + Password wird gegen DB geprüft)
- `/content` Allgemeine Content-Seite (nur nach Login)
- `/detail/<id>` Detailseite (nur Content mit mindestens 1024 Zeichen)
- `/create` New Item Page (Text wird gespeichert, nur ab mindestens 1024 Zeichen)
- `/logout` Logout und Cookie-Löschung

## Technische Hinweise

- Datenbank: SQLite-Datei `app.db`
- Auth: Cookie `name` (ohne Sessions)
- Styling: Bootstrap 5 (CDN)
