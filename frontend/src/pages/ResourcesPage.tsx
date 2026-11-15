import React, { useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Bookmark, BookmarkCheck, ExternalLink, X } from 'lucide-react';
import { apiClient } from '../api/client';
import { Resource } from '../types';
import { Skeleton } from '../components/ui/Skeleton';
import { useToast } from '../components/ui/Toast';

export const ResourcesPage: React.FC = () => {
  const [resources, setResources] = useState<Resource[]>([]);
  const toast = useToast();
  const [searchParams] = useSearchParams();
  const searchInputRef = useRef<HTMLInputElement>(null);
  const [searchInput, setSearchInput] = useState('');
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
    } catch (err: any) {
      toast.error(err.message || 'Could not load resources.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResources();
  }, [searchQuery, selectedType, selectedDifficulty]);

  // Search as you type, but only hit the API once typing pauses
  useEffect(() => {
    const timer = window.setTimeout(() => setSearchQuery(searchInput.trim()), 300);
    return () => window.clearTimeout(timer);
  }, [searchInput]);

  // The header search button and the "/" shortcut land here with ?focus=search
  useEffect(() => {
    if (searchParams.get('focus') === 'search') searchInputRef.current?.focus();
  }, [searchParams]);

  const hasFilters = searchInput !== '' || selectedType !== 'ALL';
  const clearFilters = () => {
    setSearchInput('');
    setSearchQuery('');
    setSelectedType('ALL');
  };

  const handleToggleSave = async (resourceId: string, currentSaved: boolean) => {
    // Optimistic: flip the bookmark immediately, roll back if the request fails
    setSavedMap((m) => ({ ...m, [resourceId]: !currentSaved }));
    try {
      if (currentSaved) {
        await apiClient.delete(`/resources/${resourceId}/save`);
        toast.info('Removed from your saved resources.');
      } else {
        await apiClient.post(`/resources/${resourceId}/save`);
        toast.success('Saved to your library.');
      }
    } catch (err: any) {
      setSavedMap((m) => ({ ...m, [resourceId]: currentSaved }));
      toast.error(err.message || 'Could not update your saved resources.');
    }
  };

  return (
    <div className="w-full pt-20 pb-16 bg-surface min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="mb-8">
          <span className="text-xs uppercase tracking-wider text-primary font-bold block mb-1">
            Resource library
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-on-surface">Find what you need. Skip the fluff.</h1>
          <p className="text-sm text-on-surface-variant mt-1 max-w-2xl">
Hand-picked videos, docs, courses and practice labs, ranked for your current skill gaps.
          </p>
        </div>

        {/* Filter Controls Bar */}
        <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-4 mb-8 flex flex-col md:flex-row items-center justify-between gap-4">
          
          {/* Search Bar */}
          <div className="relative w-full md:w-96">
            <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-on-surface-variant" />
            <input
              ref={searchInputRef}
              type="search"
              aria-label="Search resources"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
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
                aria-pressed={selectedType === t}
                className={`px-3 py-1.5 rounded-lg font-semibold capitalize transition-colors ${
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" role="status" aria-label="Loading resources">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-56 rounded-2xl" />
            ))}
          </div>
        ) : resources.length === 0 ? (
          <div className="bg-surface-container-lowest rounded-2xl p-10 border border-outline-variant/60 text-center">
            <Search className="w-8 h-8 text-outline mx-auto mb-3" />
            <h2 className="text-base font-bold text-on-surface mb-1">No resources match</h2>
            <p className="text-xs text-on-surface-variant mb-5">Try a broader search term or a different format.</p>
            {hasFilters && (
              <button
                type="button"
                onClick={clearFilters}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-surface-container-low text-on-surface text-xs font-bold hover:bg-surface-container transition-colors"
              >
                <X className="w-3.5 h-3.5" /> Clear filters
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resources.map((res) => {
              const isSaved = savedMap[res.id] ?? !!res.is_saved;
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
                      {res.match_score ? (
                        <span className="text-xs font-bold text-secondary bg-secondary-fixed/40 px-2 py-0.5 rounded whitespace-nowrap">
                          {Math.round(res.match_score)}% match
                        </span>
                      ) : null}
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
                      {res.duration_minutes} min
                    </span>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleToggleSave(res.id, !!isSaved)}
                        aria-label={isSaved ? `Remove ${res.title} from saved` : `Save ${res.title}`}
                        aria-pressed={!!isSaved}
                        className={`p-2 rounded-lg border border-outline-variant/60 hover:bg-surface-container-low transition-colors ${
                          isSaved ? 'text-primary bg-primary-fixed/30' : 'text-on-surface-variant'
                        }`}
                      >
                        {isSaved ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
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
