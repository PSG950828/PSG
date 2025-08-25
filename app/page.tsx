'use client';

import React, { useState } from 'react';

function interpretDream(dream: string): string[] {
  const library: Record<string, string> = {
    water: 'Emotions, intuition, and the subconscious.',
    fire: 'Transformation, passion, or potential destruction.',
    flying: 'Desire for freedom or rising above obstacles.',
    falling: 'Loss of control or insecurity in waking life.',
    snake: 'Hidden fears, worries, or transformative energy.',
    love: 'Connection, relationships, and affection.',
  };

  const lower = dream.toLowerCase();
  const matches: string[] = [];

  for (const [keyword, meaning] of Object.entries(library)) {
    if (lower.includes(keyword)) {
      matches.push(`The symbol "${keyword}" often signifies: ${meaning}`);
    }
  }

  if (matches.length === 0) {
    return [
      'No specific symbolism detected. Consider personal associations and feelings for deeper insight.',
    ];
  }

  return matches;
}

export default function Page() {
  const [dream, setDream] = useState('');
  const [interpretations, setInterpretations] = useState<string[] | null>(null);

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setInterpretations(interpretDream(dream));
  }

  return (
    <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Dream Interpreter</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
        <textarea
          value={dream}
          onChange={(e: any) => setDream(e.target.value)}
          rows={5}
          cols={40}
          placeholder="Describe your dream"
        />
        <div>
          <button type="submit" disabled={!dream.trim()}>
            Interpret
          </button>
        </div>
      </form>
      {interpretations && (
        <section>
          <h2>Interpretation</h2>
          <ul>
            {interpretations.map((line, i) => (
              <li key={i}>{line}</li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
