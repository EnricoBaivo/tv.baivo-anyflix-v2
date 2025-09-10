import { forwardRef } from "react";
import { Search, X } from "lucide-react";

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  onClose: () => void;
  placeholder?: string;
}

const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
  ({ value, onChange, onClose, placeholder = "Titles, people, genres" }, ref) => {
    return (
      <div className="flex items-center space-x-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <input
            ref={ref}
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            className="w-full bg-gray-800 text-white pl-12 pr-4 py-4 text-xl border border-gray-600 rounded focus:outline-none focus:border-white transition-colors"
          />
        </div>
        <button
          onClick={onClose}
          className="text-white hover:text-gray-300 transition-colors"
          aria-label="Close search modal"
          title="Close search modal"
        >
          <X className="h-8 w-8" />
        </button>
      </div>
    );
  }
);

SearchInput.displayName = "SearchInput";

export default SearchInput;
