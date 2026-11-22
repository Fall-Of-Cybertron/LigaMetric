'use client';

import React, { useEffect, useRef, useState } from 'react';

interface PlayerAvatarProps {
  photoUrl?: string;
  name: string;
  shirtNumber?: number;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  rounded?: 'full' | 'xl';
  className?: string;
}

const SIZE_CLASSES = {
  xs: 'w-6 h-7 text-[9px]',
  sm: 'w-7 h-9 text-[11px]',
  md: 'w-9 h-11 text-xs',
  lg: 'w-11 h-14 text-sm',
  xl: 'w-16 h-20 sm:w-20 sm:h-24 text-xl sm:text-2xl',
};

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return 'SP';
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
}

function computeObjectPosition(naturalWidth: number, naturalHeight: number): string {
  if (naturalWidth <= 0 || naturalHeight <= 0) return '50% 35%';
  const ratio = naturalHeight / naturalWidth;
  if (ratio <= 1.36) return '50% 40%';
  if (ratio <= 1.52) return '50% 42%';
  return '50% 15%';
}

export function PlayerAvatar({
  photoUrl,
  name,
  shirtNumber,
  size = 'sm',
  rounded = 'xl',
  className = '',
}: PlayerAvatarProps) {
  const [imgError, setImgError] = useState(false);
  const [objectPos, setObjectPos] = useState('50% 35%');
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    setImgError(false);
    setObjectPos('50% 35%');
    const el = imgRef.current;
    if (el && el.complete && el.naturalWidth > 0) {
      setObjectPos(computeObjectPosition(el.naturalWidth, el.naturalHeight));
    }
  }, [photoUrl]);

  const isCircular = rounded === 'full';
  const shapeClass = isCircular ? 'rounded-full' : 'rounded-xl';
  const boxSizeClass = isCircular ? 'w-full h-full text-xs' : SIZE_CLASSES[size];
  const showPhoto = Boolean(photoUrl && photoUrl.startsWith('http') && !imgError);

  if (showPhoto) {
    return (
      <span
        className={`relative inline-flex shrink-0 items-center justify-center overflow-hidden border border-[#1F2937] bg-[#090D16] shadow-sm select-none ${shapeClass} ${boxSizeClass} ${className}`}
      >
        {isCircular ? (
          <>
            <img
              src={photoUrl}
              alt=""
              aria-hidden="true"
              className="absolute inset-0 h-full w-full scale-125 object-cover opacity-45 blur-sm"
              style={{ objectPosition: objectPos }}
            />
            <img
              ref={imgRef}
              src={photoUrl}
              alt={name}
              loading="lazy"
              onLoad={(e) =>
                setObjectPos(
                  computeObjectPosition(e.currentTarget.naturalWidth, e.currentTarget.naturalHeight)
                )
              }
              onError={() => setImgError(true)}
              className="relative z-10 h-full w-[82%] object-cover"
              style={{ objectPosition: objectPos }}
            />
          </>
        ) : (
          <img
            ref={imgRef}
            src={photoUrl}
            alt={name}
            loading="lazy"
            onLoad={(e) =>
              setObjectPos(
                computeObjectPosition(e.currentTarget.naturalWidth, e.currentTarget.naturalHeight)
              )
            }
            onError={() => setImgError(true)}
            className="h-full w-full object-cover"
            style={{ objectPosition: objectPos }}
          />
        )}
      </span>
    );
  }

  const showNumber = shirtNumber !== undefined && shirtNumber > 0 && shirtNumber < 99;

  return (
    <span
      className={`inline-flex shrink-0 items-center justify-center border border-[#1F2937] bg-[#090D16] font-bold text-slate-300 tabular-nums select-none ${shapeClass} ${boxSizeClass} ${className}`}
      aria-hidden="true"
    >
      {showNumber ? shirtNumber : getInitials(name)}
    </span>
  );
}
