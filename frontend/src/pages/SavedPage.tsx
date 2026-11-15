import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Bookmark, ExternalLink, Trash2, ArrowRight } from 'lucide-react';
import { apiClient } from '../api/client';
import { Resource } from '../types';
import { Skeleton } from '../components/ui/Skeleton';
import { useToast } from '../components/ui/Toast';

export const SavedPage: React.FC = () => {
  const [savedResources, setSavedResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  const fetchSaved = async () => {
    setLoading(true);
    try {
      const res: any = await apiClient.get('/resources/user/saved');
      setSavedResources(res || []);
    } catch (err: any) {
      toast.error(err.message || 'Could not load your saved resources.');
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
      toast.info('Removed from your saved resources.');
    } catch (err: any) {
      toast.error(err.message || 'Could not remove this resource.');
    }
  };

  return (
    <div className="w-full pt-20 pb-16 bg-surface min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="mb-8">
          <span className="text-xs uppercase tracking-wider text-primary font-bold block mb-1">
            Personal Library
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-on-surface">Saved Resources</h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Bookmarked documentation, labs, and deep-dives for future reference.
          </p>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" role="status" aria-label="Loading saved resources">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-48 rounded-2xl" />
            ))}
          </div>
        ) : savedResources.length === 0 ? (
          <div className="bg-surface-container-lowest rounded-2xl p-10 border border-outline-variant/60 text-center">
            <Bookmark className="w-9 h-9 text-outline mx-auto mb-3" />
            <h2 className="text-base font-bold text-on-surface mb-1">Nothing saved yet</h2>
            <p className="text-xs text-on-surface-variant mb-5 max-w-sm mx-auto">
              Tap the bookmark on any resource to keep it here for later.
            </p>
            <Link
              to="/resources"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105 transition-all"
            >
              Browse resources <ArrowRight className="w-4 h-4" />
            </Link>
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
                      title="Remove from saved"
                      aria-label={`Remove ${res.title} from saved`}
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
