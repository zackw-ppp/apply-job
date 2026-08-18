import { ApplicationRepository } from "./applications.js";
import { createDatabase } from "./db.js";

/**
 * Seeds the database with a few example applications. Safe to run repeatedly:
 * it only inserts when the table is empty.
 */
const db = createDatabase();
const repo = new ApplicationRepository(db);

if (repo.list().length > 0) {
  console.log("Database already has applications; skipping seed.");
  process.exit(0);
}

const samples = [
  {
    company: "Vercel",
    role: "Senior Frontend Engineer",
    status: "interviewing" as const,
    location: "Remote",
    url: "https://vercel.com/careers",
    appliedOn: "2026-08-01",
    notes: "Phone screen went well; system design round next.",
  },
  {
    company: "Stripe",
    role: "Backend Engineer",
    status: "applied" as const,
    location: "Dublin, IE",
    url: "https://stripe.com/jobs",
    appliedOn: "2026-08-10",
    notes: "Referred by a former colleague.",
  },
  {
    company: "Linear",
    role: "Full-stack Engineer",
    status: "wishlist" as const,
    location: "Remote",
    notes: "Dream role — polish resume before applying.",
  },
];

for (const sample of samples) {
  repo.create(sample);
}

console.log(`Seeded ${samples.length} applications.`);
