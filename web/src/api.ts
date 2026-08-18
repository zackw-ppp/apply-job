import type { Application, ApplicationInput } from "./types";

const BASE = "/api";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `Request failed with status ${res.status}`;
    try {
      const body = await res.json();
      if (body?.error) {
        message = body.error;
        if (Array.isArray(body.details) && body.details.length > 0) {
          message += `: ${body.details.map((d: { message: string }) => d.message).join(", ")}`;
        }
      }
    } catch {
      // Response had no JSON body; keep the default message.
    }
    throw new Error(message);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

export async function listApplications(): Promise<Application[]> {
  return handle<Application[]>(await fetch(`${BASE}/applications`));
}

export async function createApplication(input: ApplicationInput): Promise<Application> {
  return handle<Application>(
    await fetch(`${BASE}/applications`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    }),
  );
}

export async function updateApplication(
  id: number,
  input: Partial<ApplicationInput>,
): Promise<Application> {
  return handle<Application>(
    await fetch(`${BASE}/applications/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    }),
  );
}

export async function deleteApplication(id: number): Promise<void> {
  return handle<void>(
    await fetch(`${BASE}/applications/${id}`, {
      method: "DELETE",
    }),
  );
}
