import React from 'react';

interface SkillAlphaLogoProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'full' | 'horizontal' | 'icon';
  showTagline?: boolean;
}

export const SkillAlphaLogo: React.FC<SkillAlphaLogoProps> = ({
  className = '',
  size = 'md',
  variant = 'horizontal',
  showTagline = false
}) => {
  // Size presets
  const sizeConfig = {
    sm: { iconSize: 26, height: 'h-7', textClass: 'text-lg', taglineClass: 'text-[7px]' },
    md: { iconSize: 34, height: 'h-9', textClass: 'text-2xl', taglineClass: 'text-[9px]' },
    lg: { iconSize: 48, height: 'h-12', textClass: 'text-3xl', taglineClass: 'text-[11px]' },
    xl: { iconSize: 64, height: 'h-16', textClass: 'text-4xl', taglineClass: 'text-[13px]' }
  };

  const currentSize = sizeConfig[size] || sizeConfig.md;

  // The geometric 'A' Icon
  const LogoIcon = (
    <svg
      width={currentSize.iconSize}
      height={currentSize.iconSize}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="flex-shrink-0 transition-transform group-hover:scale-105 duration-200"
    >
      <defs>
        {/* Right leg vibrant amber-gold gradient */}
        <linearGradient id="skillalpha-right-leg" x1="45" y1="12" x2="90" y2="88" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#F59E0B" />
          <stop offset="100%" stopColor="#D97706" />
        </linearGradient>

        {/* Faceted center triangle gradients */}
        <linearGradient id="skillalpha-facet-left" x1="48" y1="52" x2="32" y2="86" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#F59E0B" />
          <stop offset="100%" stopColor="#D97706" />
        </linearGradient>
        <linearGradient id="skillalpha-facet-right" x1="48" y1="52" x2="64" y2="86" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#FDE68A" />
          <stop offset="100%" stopColor="#F59E0B" />
        </linearGradient>
      </defs>

      {/* Left Leg: Dark Slate Navy (#0F172A / #1E293B) */}
      <path
        d="M 45 12 L 53 26 L 27 88 L 11 88 Z"
        fill="#111827"
      />

      {/* Right Leg: Warm Amber / Gold Gradient */}
      <path
        d="M 47 12 L 89 88 L 73 88 L 39 26 Z"
        fill="url(#skillalpha-right-leg)"
      />

      {/* Center Prism / Faceted Triangle - Left Facet */}
      <path
        d="M 47 52 L 32 86 L 47 86 Z"
        fill="url(#skillalpha-facet-left)"
      />

      {/* Center Prism / Faceted Triangle - Right Facet */}
      <path
        d="M 47 52 L 47 86 L 62 86 Z"
        fill="url(#skillalpha-facet-right)"
      />
    </svg>
  );

  if (variant === 'icon') {
    return <div className={`inline-flex items-center justify-center ${className}`}>{LogoIcon}</div>;
  }

  const isFull = variant === 'full' || showTagline;

  return (
    <div className={`inline-flex items-center gap-2.5 ${className}`}>
      {LogoIcon}
      <div className="flex flex-col justify-center leading-none select-none">
        <div className={`font-black tracking-tight ${currentSize.textClass} flex items-center font-sans`}>
          <span className="text-[#111827] dark:text-white">Skill</span>
          <span className="text-[#D97706]">Alpha</span>
        </div>
        {isFull && (
          <div className={`text-[#64748B] font-bold tracking-[0.24em] ${currentSize.taglineClass} mt-1 uppercase`}>
            LEARN <span className="opacity-40">|</span> PLAN <span className="opacity-40">|</span> BUILD <span className="opacity-40">|</span> GROW
          </div>
        )}
      </div>
    </div>
  );
};
