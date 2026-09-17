import React, { useEffect, useState } from 'react';
import { Bookmark, ExternalLink, Trash2 } from 'lucide-react';
import { apiClient } from '../api/client';
import { Resource } from '../types';

export const SavedPage: React.FC = () => {
  const [savedResources, setSavedResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSaved = async () => {
    setLoading(true);
    try {
      const res: any = await apiClient.get('/resources/user/saved');
      setSavedResources(res || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSaved();
  }, []);

  const handleUnsave = async (resourceId: string) => {
    try {
      await apiClient.delete(`/resources/${resourceId}/save`);
      setSavedResources(savedResources.filter(r => r.id !== resourceId));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="w-full pt-20 pb-16 bg-surface min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="mb-8">
          <span className="text-xs uppercase tracking-wider text-primary font-bold block mb-1">
            Personal Library
          </span>
          <h1 className="text-3xl font-extrabold text-on-surface">Saved Resources</h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Bookmarked documentation, labs, and deep-dives for future reference.
          </p>
        </div>

        {loading ? (
          <div className="text-center py-16 text-xs font-semibold text-on-surface-variant">
            Loading saved library...
          </div>
        ) : savedResources.length === 0 ? (
          <div className="bg-surface-container-lowest rounded-2xl p-8 border border-outline-variant/60 text-center">
            <Bookmark className="w-8 h-8 text-outline mx-auto mb-2" />
            <p className="text-sm text-on-surface-variant">No saved resources yet. Click the bookmark icon on any resource to save it here.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {savedResources.map((res) => (
              <div
                key={res.id}
                className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-6 shadow-sm flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-primary bg-primary-fixed/40 px-2 py-0.5 rounded">
                      {res.provider} • {res.resource_type}
                    </span>
                    <button
                      onClick={() => handleUnsave(res.id)}
                      className="text-error hover:bg-error-container/30 p-1 rounded transition-colors"
                      title="Unsave"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <h3 className="text-base font-bold text-on-surface mb-2">{res.title}</h3>
                  <p className="text-xs text-on-surface-variant mb-4 line-clamp-3">{res.description}</p>
                </div>

                <div className="pt-4 border-t border-outline-variant/30 flex items-center justify-between">
                  <span className="text-xs text-on-surface-variant font-medium">{res.duration_minutes} min</span>
                  <a
                    href={res.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-secondary-container text-on-primary text-xs font-bold hover:brightness-105"
                  >
                    <span>Open</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
};
