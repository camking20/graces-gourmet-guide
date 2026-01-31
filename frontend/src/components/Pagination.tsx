interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null;

  const pages: (number | string)[] = [];
  pages.push(1);
  if (currentPage > 3) pages.push('...');
  for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
    if (!pages.includes(i)) pages.push(i);
  }
  if (currentPage < totalPages - 2) pages.push('...');
  if (totalPages > 1 && !pages.includes(totalPages)) pages.push(totalPages);

  return (
    <div className="flex items-center justify-center gap-1 mt-16">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-3 py-2 text-xs text-stone hover:text-charcoal disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
      >
        Prev
      </button>

      {pages.map((page, index) => (
        <button
          key={index}
          onClick={() => typeof page === 'number' && onPageChange(page)}
          disabled={page === '...'}
          className={`min-w-[32px] px-2 py-2 text-xs transition-colors ${
            page === currentPage
              ? 'text-charcoal font-medium'
              : page === '...'
              ? 'cursor-default text-stone/50'
              : 'text-stone hover:text-charcoal'
          }`}
        >
          {page}
        </button>
      ))}

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-3 py-2 text-xs text-stone hover:text-charcoal disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
      >
        Next
      </button>
    </div>
  );
}
