export default function LoadingSpinner({ size = 'md', text }) {
  const sizes = { sm: 'w-5 h-5', md: 'w-7 h-7', lg: 'w-10 h-10' };
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12">
      <div className={`${sizes[size]} border-2 border-border border-t-accent rounded-full animate-spin`} />
      {text && <p className="text-text-muted text-sm">{text}</p>}
    </div>
  );
}
