"use client";
import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import VibeCard from './components/VibeCard';
import TagBar from './components/TagBar';

const VibeMap = dynamic(() => import('./components/VibeMap'), {
  ssr: false
});

export default function Home() {
  const [location, setLocation] = useState('');
  const [searchedLocation, setSearchedLocation] = useState('');
  const [vibeData, setVibeData] = useState(null);
  const [suggestedLocations, setSuggestedLocations] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [allLocations, setAllLocations] = useState([]);

  useEffect(() => {
    const fetchAllLocations = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/locations`);
        const data = await response.json();
        setAllLocations(data);
      } catch (error) { console.error("Failed to fetch map locations:", error); }
    };
    fetchAllLocations();
  }, []);

  const handleSearch = async (searchQuery) => {
    if (!searchQuery) return;
    setIsLoading(true);
    setVibeData(null);
    setSuggestedLocations(null);
    setSearchedLocation(searchQuery);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/vibe/${searchQuery}`);
      const data = await response.json();
      setVibeData(data);
    } catch (error) { setVibeData({ error: "Could not connect to the backend. Is it running?" }); }
    finally { setIsLoading(false); }
  };

  const handleTagSearch = async (tag) => {
    setIsLoading(true);
    setVibeData(null);
    setSuggestedLocations(null);
    setSearchedLocation(`Vibe: ${tag}`);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/locations_by_vibe/${tag}`);
      const data = await response.json();
      setSuggestedLocations(data);
    } catch (error) { console.error("Failed to fetch tag suggestions:", error); }
    finally { setIsLoading(false); }
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
    <main className="flex h-screen w-full flex-col items-center p-4 sm:p-8 bg-black/10 text-gray-800">
      <div className="text-center mb-4 flex-shrink-0">
        <h1 className="text-4xl sm:text-5xl font-extrabold mb-2 text-white drop-shadow-lg">Vibe Navigator 🔮</h1>
        <p className="text-md sm:text-lg text-gray-200 drop-shadow-md">Click a marker or search to find the vibe</p>
      </div>

      <TagBar onTagClick={handleTagSearch} />

      <div className="w-full max-w-7xl flex-grow grid grid-cols-1 md:grid-cols-3 gap-6 min-h-0">
        <div className="md:col-span-2 h-full rounded-lg shadow-lg overflow-hidden border border-gray-200">
          <VibeMap locations={allLocations} onMarkerClick={handleMarkerClick} />
        </div>

        <div className="flex flex-col gap-6 min-h-0">
          {/* --- [START] THIS FORM CODE IS NOW RESTORED --- */}
          <form onSubmit={handleFormSubmit} className="w-full">
            <div className="flex items-center bg-white rounded-full shadow-lg p-2">
              <input
                className="appearance-none bg-transparent border-none w-full text-gray-700 mr-3 py-2 px-4 leading-tight focus:outline-none"
                type="text"
                placeholder="e.g., India Gate"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
              <button
                type="submit"
                className="flex-shrink-0 bg-teal-500 hover:bg-teal-700 text-sm border-4 border-teal-500 text-white py-2 px-4 rounded-full"
                disabled={isLoading}
              >
                {isLoading ? '...' : 'Find'}
              </button>
            </div>
          </form>
          {/* --- [END] THIS FORM CODE IS NOW RESTORED --- */}

          <div className="flex-grow w-full overflow-y-auto">
            {isLoading && <p className="text-center text-white font-bold text-lg">Searching...</p>}

            {suggestedLocations && (
                <div className="w-full max-w-md p-6 rounded-xl shadow-lg bg-white/80 backdrop-blur-lg border border-white/30">
                    <h2 className="text-2xl font-bold text-gray-800">{searchedLocation}</h2>
                    {suggestedLocations.length > 0 ? (
                        <>
                            <p className="text-gray-600 mt-2 mb-4">Here are some suggested spots:</p>
                            <ul className="space-y-2">
                                {suggestedLocations.map(loc => (
                                    <li key={loc}>
                                        <button onClick={() => handleSearch(loc)} className="w-full text-left text-lg font-semibold text-teal-700 hover:text-teal-900 p-2 rounded-md hover:bg-teal-100/50">
                                            {loc}
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </>
                    ) : (
                        <p className="text-gray-600 mt-4">No spots found for this vibe. Try another!</p>
                    )}
                </div>
            )}

            {vibeData && <VibeCard vibeData={vibeData} locationName={searchedLocation} />}
          </div>
        </div>
      </div>
    </main>
  );
}