"use client";

export default function TagBar({ onTagClick }) {
  const vibeTags = ['cozy', 'lively', 'quiet', 'historic', 'creative', 'energetic'];

  return (
    <div className="w-full max-w-7xl mb-6">
        <div className="flex flex-wrap items-center justify-center gap-2">
            <span className="text-white font-semibold drop-shadow-sm">Find a vibe:</span>
            {vibeTags.map(tag => (
                <button 
                    key={tag}
                    onClick={() => onTagClick(tag)}
                    className="px-4 py-2 text-sm font-bold text-teal-800 bg-white/80 rounded-full shadow-md hover:bg-white focus:outline-none focus:ring-2 focus:ring-teal-400"
                >
                    {tag}
                </button>
            ))}
        </div>
    </div>
  );
}