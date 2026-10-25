/**
 * One measured number with its method under it. The value is tabular so a row of
 * metrics lines up; "—" while it is still being measured.
 */
export function Metric({
  label,
  value,
  note,
  met,
}: {
  label: string;
  value: string | null;
  note?: string;
  /** Whether the target was met; shown as a word, never as a colour. */
  met?: boolean | null;
}) {
  return (
    <div className="min-w-0">
      <dt className="t-micro truncate uppercase text-fg-faint">{label}</dt>
      <dd className="t-title1 tabular mt-1 truncate">{value ?? "—"}</dd>
      {(note || met !== undefined) && (
        <dd className="t-caption mt-1 text-fg-muted">
          {note}
          {met === true && <span className="ml-1 text-fg">· met</span>}
          {met === false && <span className="ml-1 text-fg">· missed</span>}
        </dd>
      )}
    </div>
  );
}
