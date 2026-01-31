import { useState, useEffect } from 'react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function SearchBar({ value, onChange, placeholder = "Search..." }: SearchBarProps) {
  const [localValue, setLocalValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      onChange(localValue);
    }, 300);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [localValue]);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  return (
    <div className="relative">
      <input
        type="text"
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        placeholder={placeholder}
        className="w-full px-0 py-3 text-base bg-transparent border-b border-sand 
                   focus:outline-none focus:border-charcoal
                   placeholder:text-stone/50 transition-colors duration-300"
      />
      {localValue && (
        <button
          onClick={() => {
            setLocalValue('');
            onChange('');
          }}
          className="absolute right-0 top-1/2 -translate-y-1/2 text-stone hover:text-charcoal transition-colors text-xs"
        >
          Clear
        </button>
      )}
    </div>
  );
}
