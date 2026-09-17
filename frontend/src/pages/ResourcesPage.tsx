import React, { useEffect, useState } from 'react';
import { Search, Filter, Bookmark, ExternalLink, Sparkles, Check } from 'lucide-react';
import { apiClient } from '../api/client';
import { Resource } from '../types';

export const ResourcesPage: React.FC = () => {
  const [resources, setResources] = useState<Resource[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);
  const [savedMap, setSavedMap] = useState<Record<string, boolean>>({});

  const fetchResources = async () => {
    setLoading(true);
    try {
      let url = '/resources?';
      if (searchQuery) url += `query=${encodeURIComponent(searchQuery)}&`;
      if (selectedType !== 'ALL') url += `resource_type=${selectedType}&`;
      if (selectedDifficulty !== 'ALL') url += `difficulty=${selectedDifficulty}&`;

      const res: any = await apiClient.get(url);
      setResources(res || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResources();
  }, [searchQuery, selectedType, selectedDifficulty]);

  const handleToggleSave = async (resourceId: string, currentSaved: boolean) => {
    try {
      if (currentSaved || savedMap[resourceId]) {
        await apiClient.delete(`/resources/${resourceId}/save`);
        setSavedMap({ ...savedMap, [resourceId]: false });
      } else {
        await apiClient.post(`/resources/${resourceId}/save`);
        setSavedMap({ ...savedMap, [resourceId]: true });
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="w-full pt-20 pb-16 bg-surface min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="mb-8">
          <span className="text-xs uppercase tracking-wider text-primary font-bold block mb-1">
            Curated Discovery Pipeline
          </span>
          <h1 className="text-3xl font-extrabold text-on-surface">Find what you need. Skip the fluff.</h1>
          <p className="text-sm text-on-surface-variant mt-1 max-w-2xl">
            Multi-source verified educational resources filtered for signal, accuracy, and topic relevance.
          </p>
        </div>

        {/* Filter Controls Bar */}
        <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-4 mb-8 flex flex-col md:flex-row items-center justify-between gap-4">
          
          {/* Search Bar */}
          <div className="relative w-full md:w-96">
            <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-on-surface-variant" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by topic, skill, or provider (e.g. Scikit-Learn, Optuna)..."
              className="w-full h-10 pl-10 pr-4 rounded-xl border border-outline-variant/60 bg-surface-container-low text-xs text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          {/* Type Filter Pills */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            {['ALL', 'DOCUMENTATION', 'VIDEO', 'PRACTICE', 'GITHUB', 'COURSE'].map((t) => (
              <button
                key={t}
                onClick={() => setSelectedType(t)}
                className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
                  selectedType === t
                    ? 'bg-primary text-on-primary shadow-sm'
                    : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container'
                }`}
              >
                {t === 'ALL' ? 'All Types' : t.toLowerCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Resource Grid */}
        {loading ? (
          <div className="text-center py-16 text-xs font-semibold text-on-surface-variant">
            Loading curated resources...
          </div>
        ) : resources.length === 0 ? (
          <div className="bg-surface-container-lowest rounded-2xl p-8 border border-outline-variant/60 text-center">
            <p className="text-sm text-on-surface-variant">We couldn't find a strong match for your filter criteria.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resources.map((res) => {
              const isSaved = savedMap[res.id] || res.is_saved;
              return (
                <div
                  key={res.id}
                  className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-6 shadow-sm flex flex-col justify-between hover:shadow-md transition-all group"
                >
                  <div>
                    {/* Header meta */}
                    <div className="flex items-center justify-between gap-2 mb-3">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-primary bg-primary-fixed/40 px-2 py-0.5 rounded">
                        {res.provider} • {res.resource_type}
                      </span>
                      <span className="text-xs font-bold text-secondary-container bg-secondary-fixed/30 px-2 py-0.5 rounded">
                        {res.match_score || 94}% match
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-on-surface group-hover:text-primary transition-colors mb-2">
                      {res.title}
                    </h3>
                    <p className="text-xs text-on-surface-variant mb-4 leading-relaxed line-clamp-3">
                      {res.description}
                    </p>

                    {res.match_reason && (
                      <div className="p-2.5 rounded-lg bg-surface-container-low text-[11px] text-on-surface-variant mb-4">
                        <strong className="text-primary block mb-0.5">Why recommended:</strong>
                        {res.match_reason}
                      </div>
                    )}
                  </div>

                  {/* Card Actions */}
                  <div className="pt-4 border-t border-outline-variant/30 flex items-center justify-between">
                    <span className="text-xs text-on-surface-variant font-medium">
                      {res.duration_minutes} min read
                    </span>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleToggleSave(res.id, !!isSaved)}
                        className={`p-2 rounded-lg border border-outline-variant/60 hover:bg-surface-container-low transition-colors ${
                          isSaved ? 'text-primary bg-primary-fixed/30' : 'text-on-surface-variant'
                        }`}
                      >
                        <Bookmark className="w-4 h-4" />
                      </button>
                      <a
                        href={res.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-secondary-container text-on-primary text-xs font-bold hover:brightness-105 transition-all"
                      >
                        <span>Open</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

      </div>
    </div>
  );
};
