export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="glass-card flex flex-col items-center justify-center px-6 py-14 text-center">
      {Icon && (
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-[#9B7AFF]/15 text-[#9B7AFF] border border-[#9B7AFF]/25">
          <Icon className="h-7 w-7" />
        </div>
      )}
      <h3 className="text-base font-semibold text-[var(--cl-text)]">{title}</h3>
      <p className="mt-1.5 max-w-md text-sm text-[var(--cl-muted)]">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
