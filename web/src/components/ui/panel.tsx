/** A quiet surface on the page for data: the table, fantasy points, the audit. */
export function Panel({
  title,
  aside,
  children,
  className = "",
}: {
  title?: React.ReactNode;
  aside?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section
      className={`rounded-panel border border-hairline bg-bg-elevated p-5 sm:p-6 ${className}`}
    >
      {(title || aside) && (
        <header className="mb-4 flex items-baseline justify-between gap-4">
          {title && <h2 className="t-title2">{title}</h2>}
          {aside && <p className="t-caption text-fg-muted">{aside}</p>}
        </header>
      )}
      {children}
    </section>
  );
}
