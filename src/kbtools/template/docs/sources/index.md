# Sources

Inbox for raw source material waiting to be ingested: decks, documents, PDFs,
spreadsheets, images, captured web pages. Follow [Ingestion](../process/ingestion.md).

- **Not in git.** Everything here is ignored except this file, `.gitignore` and
  [`ingest-log.csv`](ingest-log.csv). The log keeps each file's hash and `origin`, so anyone
  can re-fetch a source and confirm it is the same file.
- **Never edit a source.** For a new version, add a new file.
- **Naming:** `YYYY-MM-DD-short-topic.ext`. Topic subfolders are fine.
- **Logging:** run `tools/kb inventory --by <you> --origin <where it came from>` after adding files.
- **No secrets or credentials.** Check handling restrictions before you ingest confidential
  material into pages, because pages *are* committed.
