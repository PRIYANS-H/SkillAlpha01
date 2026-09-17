import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  GraduationCap, Search, Bell, User, LogOut, Shield, Compass, 
  Map, BookOpen, BookmarkCheck, BarChart3, Menu, X 
} from 'lucide-react';

interface HeaderProps {
  user?: any;
  onLogout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ user, onLogout }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);

  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  const navLinks = [
    { label: 'Roadmap', path: '/roadmap/active', icon: Map },
    { label: 'Learn Today', path: '/learn', icon: Compass },
    { label: 'Resources', path: '/resources', icon: BookOpen },
    { label: 'Progress', path: '/progress', icon: BarChart3 },
    { label: 'Saved', path: '/saved', icon: BookmarkCheck },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-surface-container-lowest/90 backdrop-blur-md border-b border-outline-variant/50">
      <div className="h-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4">
        
        {/* Brand Logo */}
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-primary-container flex items-center justify-center text-on-primary font-bold shadow-sm group-hover:scale-105 transition-transform">
              <GraduationCap className="w-5 h-5 text-on-primary" />
            </div>
            <span className="font-bold text-xl text-on-surface tracking-tight font-sans">SkillAlpha</span>
          </Link>
          <span className="hidden sm:inline-flex items-center px-2.5 py-0.5 rounded-full bg-surface-container text-on-surface-variant font-medium text-xs border border-outline-variant/40">
            adaptive learning
          </span>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1 text-sm font-medium">
          {navLinks.map((link) => {
            const active = isActive(link.path);
            const Icon = link.icon;
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors ${
                  active
                    ? 'text-primary font-semibold bg-surface-container-low'
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          
          {/* Quick Search */}
          <button
            onClick={() => navigate('/resources')}
            className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-container-low border border-outline-variant/60 text-on-surface-variant hover:text-on-surface hover:border-outline transition-colors text-left w-48 text-xs"
            type="button"
          >
            <Search className="w-4 h-4 text-on-surface-variant" />
            <span className="truncate">Search resources, topics...</span>
            <kbd className="ml-auto font-mono text-[10px] text-on-surface-variant bg-surface-container-highest px-1.5 py-0.5 rounded border border-outline-variant/40">/</kbd>
          </button>

          {/* Admin Link */}
          {user?.role === 'ADMIN' && (
            <Link
              to="/admin"
              className="hidden sm:inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-primary bg-primary-fixed/40 font-medium text-xs hover:bg-primary-fixed/70 transition-colors"
            >
              <Shield className="w-3.5 h-3.5" />
              <span>Admin</span>
            </Link>
          )}

          {/* User Menu */}
          {user ? (
            <div className="relative">
              <button
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                className="flex items-center gap-1.5 p-1 rounded-full hover:bg-surface-container-low transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-primary text-on-primary flex items-center justify-center font-semibold text-xs shadow-sm">
                  {user.full_name ? user.full_name[0].toUpperCase() : 'U'}
                </div>
              </button>

              {userDropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 rounded-xl bg-surface-container-lowest border border-outline-variant/60 shadow-lg py-1 z-50">
                  <div className="px-4 py-2 border-b border-outline-variant/40">
                    <p className="text-xs font-semibold text-on-surface truncate">{user.full_name || 'Learner'}</p>
                    <p className="text-[11px] text-on-surface-variant truncate">{user.email}</p>
                  </div>
                  <Link
                    to="/profile"
                    onClick={() => setUserDropdownOpen(false)}
                    className="flex items-center gap-2 px-4 py-2 text-xs text-on-surface hover:bg-surface-container-low transition-colors"
                  >
                    <User className="w-4 h-4" />
                    Profile & Settings
                  </Link>
                  {user.role === 'ADMIN' && (
                    <Link
                      to="/admin"
                      onClick={() => setUserDropdownOpen(false)}
                      className="flex items-center gap-2 px-4 py-2 text-xs text-primary hover:bg-surface-container-low transition-colors"
                    >
                      <Shield className="w-4 h-4" />
                      Admin Dashboard
                    </Link>
                  )}
                  <button
                    onClick={() => {
                      setUserDropdownOpen(false);
                      if (onLogout) onLogout();
                    }}
                    className="w-full flex items-center gap-2 px-4 py-2 text-xs text-error hover:bg-error-container/20 transition-colors text-left border-t border-outline-variant/40"
                  >
                    <LogOut className="w-4 h-4" />
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-on-surface hover:bg-surface-container-low transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/create"
                className="px-4 py-1.5 rounded-lg bg-secondary-container text-on-primary text-xs font-bold hover:brightness-105 transition-all shadow-sm"
              >
                Get Started
              </Link>
            </div>
          )}

          {/* Mobile Menu Trigger */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-on-surface-variant hover:bg-surface-container-low"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

        </div>
      </div>

      {/* Mobile Menu Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-surface-container-lowest border-b border-outline-variant/60 px-4 pt-2 pb-4 space-y-1">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-sm font-medium text-on-surface hover:bg-surface-container-low"
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </header>
  );
};
