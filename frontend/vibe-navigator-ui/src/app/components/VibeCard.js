"use client";
import { useState } from 'react';
import { motion } from 'framer-motion';
// --- [START] FINAL, CORRECTED IMPORT LIST ---
import { Coffee, Music, Trees, Building, Sparkles, AlertTriangle, Search, Wind, Gem, VolumeX, Wine, ShieldCheck, Users, Lightbulb, Zap, Crown, Camera, PartyPopper, Briefcase, Tent, Heart, UserCheck } from 'lucide-react';
// --- [END] FINAL, CORRECTED IMPORT LIST ---

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

// --- [START] FINAL, CORRECTED ICON MAPPING ---
const getIconComponentForTag = (tag) => {
    switch(tag) {
        case 'cozy':
        case 'coffee':
            return Coffee;
        case 'lively':
        case 'festive':
        case 'celebratory':
            return PartyPopper;
        case 'green':
        case 'peaceful':
        case 'tranquil':
        case 'serene':
        case 'natural':
        case 'calm':
            return Trees;
        case 'historic':
        case 'monumental':
        case 'classic':
        case 'traditional':
            return Building;
        case 'energetic':
            return Wind;
        case 'chic':
        case 'sophisticated':
        case 'elegant':
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
        case 'bustling':
            return Users;
        case 'grand':
        case 'impressive':
            return Crown;
        case 'touristy':
            return Camera;
        case 'productive':
            return Briefcase;
        case 'rustic':
            return Tent;
        case 'intimate':
            return Heart;
        case 'formal':
            return UserCheck; // Replaced 'Tie' with 'UserCheck'
        default:
            return Sparkles;
    }
}
// --- [END] FINAL, CORRECTED ICON MAPPING ---

export default function VibeCard({ vibeData, locationName }) {
  const [showCitations, setShowCitations] = useState(false);

  if (vibeData.error) {
    // ... No changes needed here
  }

  if (vibeData.status === 'not_found') {
    // ... No changes needed here
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
                  <li key={index} className="text-sm text-gray-800 italic">{`"${citation}"`}</li>
                ))}
              </ul>
            </motion.div>
          )}
        </div>
      )}
    </motion.div>
  );
}