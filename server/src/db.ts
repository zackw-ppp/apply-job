import { mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import Database from "better-sqlite3";

export type AppDatabase = ReturnType<typeof createDatabase>;

const DEFAULT_DB_PATH = "./data/apply-job.sqlite";

/**
 * Opens (and creates, if needed) the SQLite database used by the API.
 *
 * Pass ":memory:" for an ephemeral database, which the test suite relies on so
 * that runs never touch the developer's local data file.
 */
export function createDatabase(databasePath = process.env.DATABASE_PATH ?? DEFAULT_DB_PATH) {
  if (databasePath !== ":memory:") {
    const absolutePath = resolve(databasePath);
    mkdirSync(dirname(absolutePath), { recursive: true });
  }

  const db = new Database(databasePath);
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");

  db.exec(`
    CREATE TABLE IF NOT EXISTS applications (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      company TEXT NOT NULL,
      role TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'applied',
      location TEXT,
      url TEXT,
      notes TEXT,
      applied_on TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);

  return db;
}
