// Honeypot Component - Invisible trap for bots
// Add this to your forms, bots will fill it, humans won't

'use client';

import { useState } from 'react';

interface HoneypotProps {
  name?: string;
  onBotDetected?: () => void;
}

export function HoneypotField({ name = 'website_url', onBotDetected }: HoneypotProps) {
  return (
    <div style={{ opacity: 0, position: 'absolute', left: '-9999px' }}>
      <label htmlFor={name}>Leave this field empty</label>
      <input
        type="text"
        id={name}
        name={name}
        tabIndex={-1}
        autoComplete="off"
        onChange={(e) => {
          if (e.target.value.length > 0 && onBotDetected) {
            onBotDetected();
          }
        }}
      />
    </div>
  );
}

// CSS to hide the honeypot from humans
export const honeypotStyles = `
  .honeypot-field {
    opacity: 0;
    position: absolute;
    left: -9999px;
    pointer-events: none;
    height: 0;
    width: 0;
  }
  
  .honeypot-field input {
    height: 0;
    width: 0;
    padding: 0;
    margin: 0;
    border: none;
  }
`;

// Usage example:
// <HoneypotField name="website_url" onBotDetected={() => formRef.current?.reset()} />
