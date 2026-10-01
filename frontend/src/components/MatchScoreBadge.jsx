import React from 'react';
import { Sparkles } from 'lucide-react';

export const MatchScoreBadge = ({ score }) => {
  const rounded = Math.round(score);
  let bgColor = '#059669'; // Emerald
  if (rounded < 70) bgColor = '#d97706'; // Amber
  if (rounded < 50) bgColor = '#dc2626'; // Red

  return (
    <span
      className="match-score"
      style={{
        background: `linear-gradient(135deg, ${bgColor}, #0f172a)`,
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px'
      }}
    >
      <Sparkles size={13} />
      <span>{rounded}% Match</span>
    </span>
  );
};
