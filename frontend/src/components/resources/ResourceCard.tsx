import React, { useEffect, useState } from 'react';
import { 
  Play, ExternalLink, ThumbsUp, ThumbsDown, BookOpen, Code, 
  Video, Sparkles, Search, Layers, Clock, Check
} from 'lucide-react';
import { apiClient } from '../../api/client';

export interface ResourceItem {
  resource_id: string;
  title: string;
  url: string;
  provider: string;
  resource_type: string;
  duration_minutes?: number;
  recommendation_match_score?: number;
  recommendation_reason?: string;
}

interface ResourceCardProps {
  resource: ResourceItem;
  index?: number;
  onFeedback?: (resourceId: string, isUseful: boolean) => void;
  isFeedbackSubmitted?: boolean;
}

export const ResourceCard: React.FC<ResourceCardProps> = ({
  resource,
  index,
  onFeedback,
  isFeedbackSubmitted = false
}) => {
  const [matchData, setMatchData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedVideoIndex, setSelectedVideoIndex] = useState(0);

  useEffect(() => {
    let isMounted = true;
    const fetchMatches = async () => {
      setLoading(true);
      try {
        const queryParams = new URLSearchParams({
          name: resource.title,
          type: resource.resource_type,
          search_hint: resource.title
        });
        const res: any = await apiClient.get(`/resources/${resource.resource_id}/matches?${queryParams.toString()}`);
        if (isMounted) {
          setMatchData(res);
        }
      } catch (err) {
        if (isMounted) {
          // Graceful fallback on resolution error
          setMatchData({
            resource_id: resource.resource_id,
            type: 'fallback',
            title: resource.title,
            provider: resource.provider,
            url: resource.url,
            fallback: true
          });
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchMatches();
    return () => {
      isMounted = false;
    };
  }, [resource.resource_id, resource.title, resource.resource_type]);

  // Loading Skeleton State
  if (loading) {
    return (
      <div className="p-5 rounded-2xl bg-surface-container-low/60 border border-outline-variant/40 animate-pulse space-y-3">
        <div className="flex items-center justify-between">
          <div className="h-4 w-28 bg-surface-container-high rounded-md" />
          <div className="h-4 w-16 bg-surface-container-high rounded-md" />
        </div>
        <div className="h-5 w-3/4 bg-surface-container-high rounded-md" />
        <div className="h-3 w-1/2 bg-surface-container-high rounded-md" />
        <div className="h-32 w-full bg-surface-container-high rounded-xl" />
      </div>
    );
  }

  const isYouTube = matchData?.type === 'youtube' && matchData?.matches?.length > 0;
  const isDocsOrPractice = matchData?.type === 'docs' || matchData?.type === 'practice';
  const isBook = matchData?.type === 'book';
  const activeVideo = isYouTube ? matchData.matches[selectedVideoIndex] || matchData.matches[0] : null;

  return (
    <div className="rounded-2xl bg-surface-container-lowest border border-outline-variant/50 shadow-sm overflow-hidden transition-all hover:border-outline">
      
      {/* Card Header Bar */}
      <div className="p-4 sm:p-5 pb-3 border-b border-outline-variant/30 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2.5">
          {index !== undefined && (
            <span className="w-6 h-6 rounded-md bg-primary-fixed/50 text-primary flex items-center justify-center font-bold text-xs">
              {index + 1}
            </span>
          )}

          <div className="flex items-center gap-1.5">
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
              isYouTube ? 'bg-red-500/10 text-red-600' :
              isDocsOrPractice ? 'bg-blue-500/10 text-blue-600' :
              isBook ? 'bg-amber-500/10 text-amber-700' :
              'bg-surface-container text-on-surface-variant'
            }`}>
              {isYouTube ? '📹 Video' :
               matchData?.type === 'practice' ? '💻 Practice Lab' :
               matchData?.type === 'docs' ? '📖 Documentation' :
               isBook ? '📚 Book' : resource.resource_type}
            </span>

            <span className="text-xs text-on-surface-variant font-semibold">
              {resource.provider}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {resource.duration_minutes && (
            <span className="text-[11px] text-on-surface-variant flex items-center gap-1 bg-surface-container-low px-2 py-0.5 rounded font-medium">
              <Clock className="w-3 h-3 text-primary" /> {resource.duration_minutes}m
            </span>
          )}

          {matchData?.fallback && (
            <span className="text-[10px] text-on-surface-variant bg-surface-container px-2 py-0.5 rounded">
              Direct Link
            </span>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="p-4 sm:p-5 space-y-3">
        <div>
          <h3 className="font-bold text-base text-on-surface leading-snug">
            {activeVideo?.title || resource.title}
          </h3>
          {resource.recommendation_reason && (
            <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
              {resource.recommendation_reason}
            </p>
          )}
        </div>

        {/* 1. YouTube Video Player / Lazy-Loading Thumbnail */}
        {isYouTube && activeVideo && (
          <div className="space-y-3 pt-1">
            {!isPlaying ? (
              <div 
                onClick={() => setIsPlaying(true)}
                className="group relative aspect-video w-full rounded-xl overflow-hidden cursor-pointer bg-surface-container-high border border-outline-variant/40 shadow-inner"
              >
                <img 
                  src={activeVideo.thumbnail_url} 
                  alt={activeVideo.title}
                  className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-black/35 group-hover:bg-black/20 transition-colors flex flex-col items-center justify-center gap-2">
                  <div className="w-14 h-14 rounded-full bg-red-600/90 text-white flex items-center justify-center shadow-lg transition-transform group-hover:scale-110">
                    <Play className="w-6 h-6 fill-current ml-0.5" />
                  </div>
                  <span className="text-xs font-bold text-white tracking-wide bg-black/60 px-3 py-1 rounded-full backdrop-blur-sm">
                    Click to Play Video
                  </span>
                </div>
                <div className="absolute bottom-2 left-2 bg-black/70 text-white text-[10px] font-semibold px-2 py-0.5 rounded">
                  {activeVideo.channel_title}
                </div>
              </div>
            ) : (
              <div className="aspect-video w-full rounded-xl overflow-hidden shadow-md border border-outline-variant/40 bg-black">
                <iframe
                  className="w-full h-full"
                  src={`https://www.youtube.com/embed/${activeVideo.video_id}?autoplay=1&rel=0`}
                  title={activeVideo.title}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              </div>
            )}

            {/* Video Match Switcher (if multiple matches) */}
            {matchData.matches.length > 1 && (
              <div className="flex flex-wrap items-center gap-1.5 pt-1">
                <span className="text-[10px] text-on-surface-variant font-bold uppercase mr-1">Other Matches:</span>
                {matchData.matches.map((v: any, vIdx: number) => (
                  <button
                    key={v.video_id}
                    onClick={() => {
                      setSelectedVideoIndex(vIdx);
                      setIsPlaying(true);
                    }}
                    className={`px-2 py-1 rounded-md text-[11px] font-semibold transition-colors flex items-center gap-1 ${
                      selectedVideoIndex === vIdx
                        ? 'bg-primary text-on-primary'
                        : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container'
                    }`}
                  >
                    <span>Match {vIdx + 1}</span>
                    <span className="text-[10px] opacity-75">({v.channel_title.split(' ')[0]})</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 2. Docs or Practice Site */}
        {isDocsOrPractice && (
          <div className="p-4 rounded-xl bg-surface-container-low/70 border border-outline-variant/40 space-y-3">
            <p className="text-xs text-on-surface leading-relaxed">
              Curated documentation and interactive walkthroughs for <strong className="text-primary">{resource.title}</strong>.
            </p>
            <div className="flex flex-wrap items-center gap-2.5">
              {matchData.deep_link && (
                <a
                  href={matchData.deep_link}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-secondary-container text-on-primary font-bold text-xs hover:brightness-105 transition-all shadow-sm"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>{matchData.type === 'practice' ? 'Open Practice Lab' : 'Open Documentation'}</span>
                </a>
              )}

              {matchData.search_url && (
                <a
                  href={matchData.search_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-surface-container text-on-surface font-semibold text-xs hover:bg-surface-container-high transition-colors"
                >
                  <Search className="w-3.5 h-3.5 text-primary" />
                  <span>Search Topic on {resource.provider}</span>
                </a>
              )}
            </div>
          </div>
        )}

        {/* 3. Book Metadata */}
        {isBook && (
          <div className="p-4 rounded-xl bg-surface-container-low/70 border border-outline-variant/40 space-y-2.5">
            <div className="text-xs text-on-surface">
              <span className="font-bold text-primary mr-1">Publisher / Author:</span>
              <span>{matchData.author || resource.provider}</span>
            </div>
            {matchData.description && (
              <p className="text-xs text-on-surface-variant leading-relaxed">
                {matchData.description}
              </p>
            )}
            {matchData.topics && matchData.topics.length > 0 && (
              <div>
                <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block mb-1.5">
                  Core Topics & Chapters Covered
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {matchData.topics.map((top: string, tIdx: number) => (
                    <span 
                      key={tIdx} 
                      className="px-2 py-0.5 rounded-md bg-surface-container text-on-surface text-[11px] font-medium"
                    >
                      {top}
                    </span>
                  ))}
                </div>
              </div>
            )}
            <p className="text-[11px] text-on-surface-variant italic pt-1">
              Official textbook reference — consult the chapters highlighted in your curriculum plan.
            </p>
          </div>
        )}

        {/* 4. Fallback Raw Resource */}
        {!isYouTube && !isDocsOrPractice && !isBook && (
          <div className="pt-1">
            <a
              href={resource.url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-surface-container text-on-surface font-semibold text-xs hover:bg-surface-container-high transition-colors"
            >
              <span>Visit External Resource</span>
              <ExternalLink className="w-3.5 h-3.5 text-primary" />
            </a>
          </div>
        )}

      </div>

      {/* Footer Feedback Bar */}
      {onFeedback && (
        <div className="px-4 sm:px-5 py-2.5 bg-surface-container-low/40 border-t border-outline-variant/30 flex items-center justify-between text-xs text-on-surface-variant">
          <span className="text-[11px]">Was this resource helpful?</span>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => onFeedback(resource.resource_id, true)}
              className={`p-1.5 rounded-lg transition-colors flex items-center gap-1 ${
                isFeedbackSubmitted ? 'text-primary bg-primary-fixed/40' : 'hover:bg-surface-container text-on-surface-variant'
              }`}
              title="Helpful"
            >
              <ThumbsUp className="w-3.5 h-3.5" />
              {isFeedbackSubmitted && <span className="text-[10px] font-bold">Feedback Sent</span>}
            </button>
            <button
              onClick={() => onFeedback(resource.resource_id, false)}
              className="p-1.5 rounded-lg hover:bg-error-container/40 text-on-surface-variant transition-colors"
              title="Not relevant"
            >
              <ThumbsDown className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

    </div>
  );
};
