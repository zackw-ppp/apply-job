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

export interface ApplicationInput {
  company: string;
  role: string;
  status: Status;
  location?: string;
  url?: string;
  notes?: string;
  appliedOn?: string;
}

export const STATUS_LABELS: Record<Status, string> = {
  wishlist: "Wishlist",
  applied: "Applied",
  interviewing: "Interviewing",
  offer: "Offer",
  rejected: "Rejected",
};
