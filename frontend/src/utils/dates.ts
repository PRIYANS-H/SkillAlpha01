/** Parses a backend ISO date ("2026-11-04") as a local calendar date (no timezone shift). */
export const parseDueDate = (iso?: string | null): Date | null => {
  if (!iso) return null;
  const [y, m, d] = iso.split('-').map(Number);
  if (!y || !m || !d) return null;
  return new Date(y, m - 1, d);
};

export const formatDueDate = (iso?: string | null): string => {
  const date = parseDueDate(iso);
  return date ? date.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' }) : '';
};

const startOfToday = (): Date => {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), now.getDate());
};

/** True when a not-yet-finished task's due date is before today. */
export const isOverdue = (iso?: string | null, status?: string): boolean => {
  const date = parseDueDate(iso);
  if (!date || status === 'COMPLETED' || status === 'SKIPPED') return false;
  return date < startOfToday();
};

/** "Nov 04 – Nov 08" across the given ISO dates, or '' if none are set. */
export const formatDateRange = (isos: (string | null | undefined)[]): string => {
  const dates = isos.map(parseDueDate).filter((d): d is Date => d !== null).sort((a, b) => a.getTime() - b.getTime());
  if (dates.length === 0) return '';
  const fmt = (d: Date) => d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  const first = fmt(dates[0]);
  const last = fmt(dates[dates.length - 1]);
  return first === last ? first : `${first} – ${last}`;
};
