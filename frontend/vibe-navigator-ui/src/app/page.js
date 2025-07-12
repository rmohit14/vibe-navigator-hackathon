"use client";
import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import VibeCard from './components/VibeCard';

const VibeMap = dynamic(() => import('./components/VibeMap'), {
  ssr: false
});

export default function Home() {
  const [location, setLocation] = useState('');
  const [searchedLocation, setSearchedLocation] = useState('');
  const [vibeData, setVibeData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [allLocations, setAllLocations] = useState([]);

  useEffect(() => {
    const fetchAllLocations = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/locations`);
        const data = await response.json();
        setAllLocations(data);
      } catch (error) {
        console.error("Failed to fetch locations for map:", error);
      }
    };
    fetchAllLocations();
  }, []);

  const handleSearch = async (searchQuery) => {
    if (!searchQuery) return;

    setIsLoading(true);
    setVibeData(null);
    setSearchedLocation(searchQuery);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/vibe/${searchQuery}`);
      const data = await response.json();
      setVibeData(data);
    } catch (error) {
      setVibeData({ error: "Could not connect to the backend. Is it running?" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    handleSearch(location);
  };

  const handleMarkerClick = (locationName) => {
    setLocation(locationName);
    handleSearch(locationName);
  };

  return (
    // --- THE CHANGE IS ON THIS LINE: Removed gradient, added subtle overlay for readability ---
    <main className="flex h-screen w-full flex-col items-center p-4 sm:p-8 text-gray-800 bg-black/10">
      <div className="text-center mb-4 flex-shrink-0">
        {/* --- Updated text color for better contrast on an image --- */}
        <h1 className="text-4xl sm:text-5xl font-extrabold mb-2 text-white drop-shadow-lg">Vibe Navigator 🔮</h1>
        <p className="text-md sm:text-lg text-gray-200 drop-shadow-md">Click a marker or search to find the vibe</p>
      </div>

      <div className="w-full max-w-7xl flex-grow grid grid-cols-1 md:grid-cols-3 gap-6 min-h-0">
        {/* Map Column */}
        <div className="md:col-span-2 h-full rounded-lg shadow-lg overflow-hidden border border-gray-200">
          <VibeMap locations={allLocations} onMarkerClick={handleMarkerClick} />
        </div>

        {/* Search and Results Column */}
        <div className="flex flex-col gap-6 min-h-0">
          <form onSubmit={handleFormSubmit} className="w-full">
            <div className="flex items-center bg-white rounded-full shadow-lg p-2">
              <input
                className="appearance-none bg-transparent border-none w-full text-gray-700 mr-3 py-2 px-4 leading-tight focus:outline-none"
                type="text"
                placeholder="e.g., The Cozy Mug Cafe"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
              <button
                className="flex-shrink-0 bg-teal-500 hover:bg-teal-700 border-teal-500 hover:border-teal-700 text-sm border-4 text-white py-2 px-4 rounded-full disabled:bg-gray-400"
                type="submit"
                disabled={isLoading}
              >
                {isLoading ? '...' : 'Find'}
              </button>
            </div>
          </form>

          <div className="flex-grow w-full overflow-y-auto">
            {isLoading && (
                <div className="w-full p-6 text-center text-white font-bold text-lg drop-shadow-md">
                    Getting the vibe...
                </div>
            )}
            {vibeData && <VibeCard vibeData={vibeData} locationName={searchedLocation} />}
          </div>
        </div>
      </div>
    </main>
  );
}