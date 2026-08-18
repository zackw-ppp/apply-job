import { z } from "zod";
import type { AppDatabase } from "./db.js";

export const STATUSES = [
  "wishlist",
  "applied",
  "interviewing",
  "offer",
  "rejected",
] as const;

export type Status = (typeof STATUSES)[number];

export interface Application {
  id: number;
  company: string;
  role: string;
  status: Status;
  location: string | null;
  url: string | null;
  notes: string | null;
  appliedOn: string | null;
  createdAt: string;
  updatedAt: string;
}

interface ApplicationRow {
  id: number;
  company: string;
  role: string;
  status: Status;
  location: string | null;
  url: string | null;
  notes: string | null;
  applied_on: string | null;
  created_at: string;
  updated_at: string;
}

const baseSchema = z.object({
  company: z.string().trim().min(1, "company is required").max(200),
  role: z.string().trim().min(1, "role is required").max(200),
  status: z.enum(STATUSES).default("applied"),
  location: z.string().trim().max(200).optional().nullable(),
  url: z.string().trim().url("url must be a valid URL").max(500).optional().or(z.literal("")).nullable(),
  notes: z.string().trim().max(5000).optional().nullable(),
  appliedOn: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, "appliedOn must be an ISO date (YYYY-MM-DD)")
    .optional()
    .or(z.literal(""))
    .nullable(),
});

export const createApplicationSchema = baseSchema;
export const updateApplicationSchema = baseSchema.partial();

export type CreateApplicationInput = z.infer<typeof createApplicationSchema>;
export type UpdateApplicationInput = z.infer<typeof updateApplicationSchema>;

function normalizeOptional(value: string | null | undefined): string | null {
  if (value === undefined || value === null) return null;
  const trimmed = value.trim();
  return trimmed === "" ? null : trimmed;
}

function rowToApplication(row: ApplicationRow): Application {
  return {
    id: row.id,
    company: row.company,
    role: row.role,
    status: row.status,
    location: row.location,
    url: row.url,
    notes: row.notes,
    appliedOn: row.applied_on,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

export class ApplicationRepository {
  constructor(private readonly db: AppDatabase) {}

  list(): Application[] {
    const rows = this.db
      .prepare(
        `SELECT * FROM applications
         ORDER BY datetime(updated_at) DESC, id DESC`,
      )
      .all() as ApplicationRow[];
    return rows.map(rowToApplication);
  }

  get(id: number): Application | null {
    const row = this.db
      .prepare(`SELECT * FROM applications WHERE id = ?`)
      .get(id) as ApplicationRow | undefined;
    return row ? rowToApplication(row) : null;
  }

  create(input: CreateApplicationInput): Application {
    const result = this.db
      .prepare(
        `INSERT INTO applications (company, role, status, location, url, notes, applied_on)
         VALUES (@company, @role, @status, @location, @url, @notes, @appliedOn)`,
      )
      .run({
        company: input.company,
        role: input.role,
        status: input.status ?? "applied",
        location: normalizeOptional(input.location),
        url: normalizeOptional(input.url),
        notes: normalizeOptional(input.notes),
        appliedOn: normalizeOptional(input.appliedOn),
      });

    const created = this.get(Number(result.lastInsertRowid));
    if (!created) {
      throw new Error("Failed to load application after insert");
    }
    return created;
  }

  update(id: number, input: UpdateApplicationInput): Application | null {
    const existing = this.get(id);
    if (!existing) return null;

    const merged = {
      company: input.company ?? existing.company,
      role: input.role ?? existing.role,
      status: input.status ?? existing.status,
      location:
        input.location === undefined ? existing.location : normalizeOptional(input.location),
      url: input.url === undefined ? existing.url : normalizeOptional(input.url),
      notes: input.notes === undefined ? existing.notes : normalizeOptional(input.notes),
      appliedOn:
        input.appliedOn === undefined ? existing.appliedOn : normalizeOptional(input.appliedOn),
    };

    this.db
      .prepare(
        `UPDATE applications
         SET company = @company,
             role = @role,
             status = @status,
             location = @location,
             url = @url,
             notes = @notes,
             applied_on = @appliedOn,
             updated_at = datetime('now')
         WHERE id = @id`,
      )
      .run({ ...merged, id });

    return this.get(id);
  }

  delete(id: number): boolean {
    const result = this.db.prepare(`DELETE FROM applications WHERE id = ?`).run(id);
    return result.changes > 0;
  }
}
