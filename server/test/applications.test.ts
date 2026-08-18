import { afterEach, beforeEach, describe, expect, it } from "vitest";
import request from "supertest";
import type { Express } from "express";
import { createApp } from "../src/app.js";
import { createDatabase, type AppDatabase } from "../src/db.js";

describe("applications API", () => {
  let db: AppDatabase;
  let app: Express;

  beforeEach(() => {
    db = createDatabase(":memory:");
    app = createApp(db);
  });

  afterEach(() => {
    db.close();
  });

  it("starts with an empty list", async () => {
    const res = await request(app).get("/api/applications");
    expect(res.status).toBe(200);
    expect(res.body).toEqual([]);
  });

  it("creates an application and returns it", async () => {
    const res = await request(app)
      .post("/api/applications")
      .send({ company: "Acme", role: "Backend Engineer", status: "applied" });

    expect(res.status).toBe(201);
    expect(res.body).toMatchObject({
      id: expect.any(Number),
      company: "Acme",
      role: "Backend Engineer",
      status: "applied",
    });

    const list = await request(app).get("/api/applications");
    expect(list.body).toHaveLength(1);
  });

  it("rejects invalid payloads with a 400", async () => {
    const res = await request(app).post("/api/applications").send({ role: "Missing company" });
    expect(res.status).toBe(400);
    expect(res.body.error).toBe("Validation failed");
  });

  it("rejects an invalid status enum", async () => {
    const res = await request(app)
      .post("/api/applications")
      .send({ company: "Acme", role: "Dev", status: "banana" });
    expect(res.status).toBe(400);
  });

  it("updates an application's status", async () => {
    const created = await request(app)
      .post("/api/applications")
      .send({ company: "Globex", role: "SRE" });

    const updated = await request(app)
      .patch(`/api/applications/${created.body.id}`)
      .send({ status: "interviewing" });

    expect(updated.status).toBe(200);
    expect(updated.body.status).toBe("interviewing");
  });

  it("returns 404 when updating a missing application", async () => {
    const res = await request(app).patch("/api/applications/9999").send({ status: "offer" });
    expect(res.status).toBe(404);
  });

  it("deletes an application", async () => {
    const created = await request(app)
      .post("/api/applications")
      .send({ company: "Initech", role: "PM" });

    const del = await request(app).delete(`/api/applications/${created.body.id}`);
    expect(del.status).toBe(204);

    const list = await request(app).get("/api/applications");
    expect(list.body).toHaveLength(0);
  });

  it("exposes a health endpoint", async () => {
    const res = await request(app).get("/api/health");
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ status: "ok" });
  });
});
