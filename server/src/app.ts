import cors from "cors";
import express, { type Request, type Response, type NextFunction } from "express";
import { ZodError } from "zod";
import {
  ApplicationRepository,
  createApplicationSchema,
  updateApplicationSchema,
} from "./applications.js";
import type { AppDatabase } from "./db.js";

export function createApp(db: AppDatabase) {
  const app = express();
  const repo = new ApplicationRepository(db);

  app.use(express.json());
  app.use(
    cors({
      origin: process.env.CORS_ORIGIN ?? "http://localhost:5173",
    }),
  );

  app.get("/api/health", (_req, res) => {
    res.json({ status: "ok" });
  });

  app.get("/api/applications", (_req, res) => {
    res.json(repo.list());
  });

  app.post("/api/applications", (req, res) => {
    const input = createApplicationSchema.parse(req.body);
    const application = repo.create(input);
    res.status(201).json(application);
  });

  app.get("/api/applications/:id", (req, res) => {
    const application = repo.get(Number(req.params.id));
    if (!application) {
      res.status(404).json({ error: "Application not found" });
      return;
    }
    res.json(application);
  });

  app.patch("/api/applications/:id", (req, res) => {
    const input = updateApplicationSchema.parse(req.body);
    const application = repo.update(Number(req.params.id), input);
    if (!application) {
      res.status(404).json({ error: "Application not found" });
      return;
    }
    res.json(application);
  });

  app.delete("/api/applications/:id", (req, res) => {
    const deleted = repo.delete(Number(req.params.id));
    if (!deleted) {
      res.status(404).json({ error: "Application not found" });
      return;
    }
    res.status(204).end();
  });

  // Centralized error handling: validation errors become 400s.
  app.use((err: unknown, _req: Request, res: Response, _next: NextFunction) => {
    if (err instanceof ZodError) {
      res.status(400).json({
        error: "Validation failed",
        details: err.issues.map((issue) => ({
          path: issue.path.join("."),
          message: issue.message,
        })),
      });
      return;
    }

    console.error(err);
    res.status(500).json({ error: "Internal server error" });
  });

  return app;
}
