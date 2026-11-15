import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Map, Compass, BookOpen, BarChart3, BookmarkCheck } from 'lucide-react';

const TABS = [
  { label: 'Roadmap', path: '/roadmap/active', match: '/roadmap', icon: Map },
  { label: 'Today', path: '/learn', match: '/learn', icon: Compass },
  { label: 'Resources', path: '/resources', match: '/resources', icon: BookOpen },
  { label: 'Progress', path: '/progress', match: '/progress', icon: BarChart3 },
  { label: 'Saved', path: '/saved', match: '/saved', icon: BookmarkCheck },
];

/** Thumb-reachable primary navigation on phones (the header nav is desktop-only). */
export const MobileTabBar: React.FC = () => {
  const { pathname } = useLocation();
  return (
    <nav
      aria-label="Primary"
      className="md:hidden fixed bottom-0 inset-x-0 z-50 bg-surface-container-lowest/95 backdrop-blur-md border-t border-outline-variant pb-[env(safe-area-inset-bottom)]"
    >
      <ul className="grid grid-cols-5">
        {TABS.map(({ label, path, match, icon: Icon }) => {
          const active = pathname.startsWith(match);
          return (
            <li key={path}>
              <Link
                to={path}
                aria-current={active ? 'page' : undefined}
                className={`flex flex-col items-center gap-0.5 py-2 text-[10px] font-semibold transition-colors ${
                  active ? 'text-primary' : 'text-on-surface-variant'
                }`}
              >
                <span className={`px-4 py-1 rounded-full transition-colors ${active ? 'bg-primary-fixed/60' : ''}`}>
                  <Icon className="w-5 h-5" />
                </span>
                {label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
};
