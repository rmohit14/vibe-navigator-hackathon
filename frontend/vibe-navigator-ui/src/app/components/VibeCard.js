"use client";
import { useState } from 'react';
import { motion } from 'framer-motion';
// --- [START] THIS IMPORT LIST INCLUDES THE ICONS FOR THE NEW TAGS ---
import { Coffee, Music, Trees, Building, Sparkles, AlertTriangle, Search, Wind, Gem, VolumeX, Wine, ShieldCheck, Users, Lightbulb, Zap } from 'lucide-react';
// --- [END] THIS IMPORT LIST INCLUDES THE ICONS FOR THE NEW TAGS ---

const getVibeTheme = (tag) => {
    // This function is correct
    switch (tag) {
        case 'lively': case 'energetic': case 'festive':
          return 'from-yellow-500/30 to-orange-400/30 border-yellow-300/50';
        case 'cozy': case 'historic':
          return 'from-amber-500/30 to-orange-500/30 border-amber-400/50';
        case 'peaceful': case 'tranquil': case 'green':
          return 'from-emerald-500/30 to-green-400/30 border-emerald-300/50';
        case 'monumental': case 'patriotic':
          return 'from-blue-500/30 to-sky-400/30 border-blue-300/50';
        default:
          return 'from-gray-400/30 to-gray-200/30 border-gray-300/50';
    }
};

// --- [START] THIS FUNCTION IS UPDATED WITH THE FINAL CASES ---
const getIconComponentForTag = (tag) => {
    switch(tag) {
        case 'cozy':
        case 'coffee':
            return Coffee;
        case 'lively':
        case 'festive':
            return Music;
        case 'green':
        case 'peaceful':
        case 'tranquil':
            return Trees;
        case 'historic':
        case 'monumental':
            return Building;
        case 'energetic':
            return Wind;
        case 'chic':
        case 'sophisticated':
            return Gem;
        case 'quiet':
            return VolumeX;
        case 'patriotic':
            return ShieldCheck;
        case 'vibrant':
            return Zap;
        case 'creative':
            return Lightbulb;
        case 'crowded':
            return Users;
        default:
            return Sparkles;
    }
}
// --- [END] THIS FUNCTION IS UPDATED ---

export default function VibeCard({ vibeData, locationName }) {
  const [showCitations, setShowCitations] = useState(false);

  if (vibeData.error) {
    // Error handling is correct
    return (
        <motion.div 
          className="w-full max-w-md p-6 rounded-xl shadow-lg bg-red-500/50 backdrop-blur-lg border border-red-300/50 text-white"
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
        >
          <div className="flex items-center gap-3">
              <AlertTriangle className="w-8 h-8"/>
              <p className="font-bold text-lg">An Error Occurred</p>
          </div>
          <p className="mt-2">{vibeData.error}</p>
        </motion.div>
    );
  }

  if (vibeData.status === 'not_found') {
    // "Not found" handling is correct
    return (
      <motion.div 
        className="w-full max-w-md p-6 rounded-xl shadow-lg bg-white/50 backdrop-blur-lg border border-white/30"
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
      >
        <div className="flex items-center gap-3 mb-4">
            <Search className="w-8 h-8 text-gray-700"/>
            <h2 className="text-2xl font-bold text-gray-800">Hmm...</h2>
        </div>
        <p className="text-gray-700 my-4">{vibeData.message || `I couldn't find anything about "${locationName}".`}</p>
        {vibeData.suggestions && vibeData.suggestions.length > 0 && (
          <div>
            <h3 className="font-semibold text-gray-700">Perhaps you'd be interested in these spots?</h3>
            <ul className="list-disc list-inside mt-2 text-teal-700 font-medium">
              {vibeData.suggestions.map((suggestion, index) => (
                <li key={index}>{suggestion}</li>
              ))}
            </ul>
          </div>
        )}
      </motion.div>
    );
  }

  const { summary, tags, citations } = vibeData;
  const cardTheme = getVibeTheme(tags ? tags[0].trim().toLowerCase() : '');

  return (
    <motion.div
      className={`w-full max-w-md p-6 rounded-xl shadow-lg backdrop-blur-lg border bg-gradient-to-br ${cardTheme}`}
      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
    >
      <h2 className="text-3xl font-bold text-gray-900 drop-shadow-sm">{locationName}</h2>

      <div className="flex items-center space-x-3 my-4">
        {tags && tags.slice(0, 4).map((tag, index) => {
          const IconComponent = getIconComponentForTag(tag.trim().toLowerCase());
          return <IconComponent key={index} className="w-7 h-7" />;
        })}
      </div>

      <p className="text-gray-800 font-medium mb-4">{summary}</p>

      <div className="flex flex-wrap gap-2 mb-6">
        {tags && tags.map((tag, index) => (
          <motion.span
            key={index}
            className="px-3 py-1 bg-black/10 text-gray-900 text-sm font-semibold rounded-full"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.2 + index * 0.1 }}
          >
            {tag}
          </motion.span>
        ))}
      </div>

      {citations && citations.length > 0 && (
        <div>
          <button
            onClick={() => setShowCitations(!showCitations)}
            className="text-sm font-bold text-gray-800 hover:text-black focus:outline-none"
          >
            {showCitations ? 'Hide Source Reviews' : 'Show Source Reviews'} ▼
          </button>
          {showCitations && (
            <motion.div 
                className="mt-3 p-3 bg-black/10 rounded-lg"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
            >
              <h4 className="font-semibold text-xs text-gray-700 mb-2">Based on these reviews:</h4>
              <ul className="list-disc list-inside space-y-2">
                {citations.map((citation, index) => (
                  <li key={index} className="text-sm text-gray-800 italic">"{citation}"</li>
                ))}
              </ul>
            </motion.div>
          )}
        </div>
      )}
    </motion.div>
  );
}