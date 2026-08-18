import { useEffect, useMemo, useState } from "react";
import {
  createApplication,
  deleteApplication,
  listApplications,
  updateApplication,
} from "./api";
import { STATUS_LABELS, STATUSES, type Application, type Status } from "./types";

const EMPTY_FORM = {
  company: "",
  role: "",
  status: "applied" as Status,
  location: "",
  url: "",
  appliedOn: "",
  notes: "",
};

export default function App() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [form, setForm] = useState({ ...EMPTY_FORM });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [filter, setFilter] = useState<Status | "all">("all");

  async function refresh() {
    try {
      setError(null);
      const data = await listApplications();
      setApplications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load applications");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  const counts = useMemo(() => {
    const base: Record<Status, number> = {
      wishlist: 0,
      applied: 0,
      interviewing: 0,
      offer: 0,
      rejected: 0,
    };
    for (const app of applications) {
      base[app.status] += 1;
    }
    return base;
  }, [applications]);

  const visible = useMemo(
    () => (filter === "all" ? applications : applications.filter((a) => a.status === filter)),
    [applications, filter],
  );

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await createApplication({
        company: form.company,
        role: form.role,
        status: form.status,
        location: form.location || undefined,
        url: form.url || undefined,
        appliedOn: form.appliedOn || undefined,
        notes: form.notes || undefined,
      });
      setForm({ ...EMPTY_FORM });
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create application");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusChange(app: Application, status: Status) {
    setApplications((prev) => prev.map((a) => (a.id === app.id ? { ...a, status } : a)));
    try {
      await updateApplication(app.id, { status });
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update status");
      await refresh();
    }
  }

  async function handleDelete(app: Application) {
    if (!confirm(`Delete your ${app.role} application at ${app.company}?`)) return;
    try {
      await deleteApplication(app.id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete application");
    }
  }

  return (
    <div className="page">
      <header className="masthead">
        <div className="masthead__brand">
          <span className="masthead__logo" aria-hidden>✓</span>
          <div>
            <h1>apply-job</h1>
            <p>Track every application from wishlist to offer.</p>
          </div>
        </div>
        <div className="masthead__total">
          <span className="masthead__total-number">{applications.length}</span>
          <span className="masthead__total-label">total</span>
        </div>
      </header>

      <section className="stats" aria-label="Application counts by status">
        {STATUSES.map((status) => (
          <button
            key={status}
            type="button"
            className={`stat stat--${status} ${filter === status ? "stat--active" : ""}`}
            onClick={() => setFilter((current) => (current === status ? "all" : status))}
          >
            <span className="stat__count">{counts[status]}</span>
            <span className="stat__label">{STATUS_LABELS[status]}</span>
          </button>
        ))}
      </section>

      <div className="layout">
        <section className="card form-card">
          <h2>Add an application</h2>
          <form onSubmit={handleSubmit} className="form">
            <label className="field">
              <span>Company *</span>
              <input
                required
                value={form.company}
                onChange={(e) => setForm({ ...form, company: e.target.value })}
                placeholder="Acme Corp"
              />
            </label>
            <label className="field">
              <span>Role *</span>
              <input
                required
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
                placeholder="Backend Engineer"
              />
            </label>
            <div className="field-row">
              <label className="field">
                <span>Status</span>
                <select
                  value={form.status}
                  onChange={(e) => setForm({ ...form, status: e.target.value as Status })}
                >
                  {STATUSES.map((status) => (
                    <option key={status} value={status}>
                      {STATUS_LABELS[status]}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Applied on</span>
                <input
                  type="date"
                  value={form.appliedOn}
                  onChange={(e) => setForm({ ...form, appliedOn: e.target.value })}
                />
              </label>
            </div>
            <label className="field">
              <span>Location</span>
              <input
                value={form.location}
                onChange={(e) => setForm({ ...form, location: e.target.value })}
                placeholder="Remote"
              />
            </label>
            <label className="field">
              <span>Posting URL</span>
              <input
                type="url"
                value={form.url}
                onChange={(e) => setForm({ ...form, url: e.target.value })}
                placeholder="https://…"
              />
            </label>
            <label className="field">
              <span>Notes</span>
              <textarea
                rows={3}
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                placeholder="Referral, contacts, next steps…"
              />
            </label>
            <button className="button button--primary" type="submit" disabled={submitting}>
              {submitting ? "Saving…" : "Add application"}
            </button>
          </form>
        </section>

        <section className="card list-card">
          <div className="list-card__header">
            <h2>
              {filter === "all" ? "All applications" : STATUS_LABELS[filter]}
              <span className="list-card__count">{visible.length}</span>
            </h2>
            {filter !== "all" && (
              <button type="button" className="button button--ghost" onClick={() => setFilter("all")}>
                Clear filter
              </button>
            )}
          </div>

          {error && <p className="error" role="alert">{error}</p>}

          {loading ? (
            <p className="muted">Loading…</p>
          ) : visible.length === 0 ? (
            <div className="empty">
              <p className="empty__title">No applications yet</p>
              <p className="muted">Add your first application using the form to get started.</p>
            </div>
          ) : (
            <ul className="applications">
              {visible.map((app) => (
                <li key={app.id} className="application">
                  <div className="application__main">
                    <div>
                      <p className="application__role">{app.role}</p>
                      <p className="application__company">
                        {app.company}
                        {app.location ? ` · ${app.location}` : ""}
                      </p>
                    </div>
                    <span className={`badge badge--${app.status}`}>{STATUS_LABELS[app.status]}</span>
                  </div>

                  {app.notes && <p className="application__notes">{app.notes}</p>}

                  <div className="application__meta">
                    {app.appliedOn && <span>Applied {app.appliedOn}</span>}
                    {app.url && (
                      <a href={app.url} target="_blank" rel="noreferrer">
                        View posting ↗
                      </a>
                    )}
                  </div>

                  <div className="application__actions">
                    <label className="inline-field">
                      <span>Status</span>
                      <select
                        value={app.status}
                        onChange={(e) => handleStatusChange(app, e.target.value as Status)}
                      >
                        {STATUSES.map((status) => (
                          <option key={status} value={status}>
                            {STATUS_LABELS[status]}
                          </option>
                        ))}
                      </select>
                    </label>
                    <button
                      type="button"
                      className="button button--danger"
                      onClick={() => handleDelete(app)}
                    >
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
