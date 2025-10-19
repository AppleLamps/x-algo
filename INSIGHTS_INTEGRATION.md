# Rotating Insights Feature - Frontend Integration Guide

## Overview
The `/insights` endpoint generates 8-12 quick, interesting observations about a user's X account using **grok-3**. These insights are designed to rotate every 4 seconds while the main analysis is running.

## Backend Endpoint

### POST `/insights`

**Request:**
```json
{
  "username": "elonmusk"
}
```

**Response:**
```json
{
  "insights": [
    "You engage most with accounts under 10K followers, suggesting you prefer authentic voices over influencers.",
    "Your posting activity peaks on weekday mornings, indicating a professional content strategy.",
    "You reply more than you retweet, showing a preference for genuine conversation over amplification.",
    "Your interests span both technical depth and creative expression—a rare combination.",
    "Recent activity shows emerging interest in AI tools, marking a shift from purely theoretical discussions.",
    "You consistently engage with niche technical content over mainstream viral posts.",
    "Strong network clustering around aerospace and tech innovation communities.",
    "Your engagement patterns suggest you're an early adopter rather than trend follower."
  ]
}
```

## Frontend Implementation Guide

### Recommended Flow

1. **User submits username** → Call both endpoints in parallel:
   - `POST /analyze` (main analysis - takes longer)
   - `POST /insights` (quick insights - returns faster)

2. **Display rotating insights** while `/analyze` is loading:
   - Rotate through insights every **4 seconds**
   - Show a subtle fade transition between insights
   - Display in the area where "Analyzing your profile..." spinner currently is

3. **When `/analyze` completes** → Replace insights with full results

### Example React Implementation

```typescript
import { useState, useEffect } from 'react';

interface InsightsDisplayProps {
  username: string;
  isAnalyzing: boolean;
}

export function InsightsDisplay({ username, isAnalyzing }: InsightsDisplayProps) {
  const [insights, setInsights] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  // Fetch insights when component mounts
  useEffect(() => {
    const fetchInsights = async () => {
      try {
        const response = await fetch('http://localhost:8000/insights', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || '',
          },
          body: JSON.stringify({ username }),
        });
        
        const data = await response.json();
        setInsights(data.insights);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch insights:', error);
        // Fallback to generic loading message
        setInsights(['Analyzing your profile...']);
        setLoading(false);
      }
    };

    if (isAnalyzing) {
      fetchInsights();
    }
  }, [username, isAnalyzing]);

  // Rotate insights every 4 seconds
  useEffect(() => {
    if (!isAnalyzing || insights.length === 0) return;

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % insights.length);
    }, 4000);

    return () => clearInterval(interval);
  }, [isAnalyzing, insights.length]);

  if (!isAnalyzing) return null;

  return (
    <div className="flex items-center justify-center min-h-[200px]">
      <div className="max-w-2xl text-center space-y-4">
        {/* Spinner */}
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
        </div>
        
        {/* Rotating insight */}
        <div className="transition-opacity duration-500 ease-in-out">
          <p className="text-lg text-gray-700 dark:text-gray-300">
            {loading ? 'Loading insights...' : insights[currentIndex]}
          </p>
        </div>
        
        {/* Progress indicator */}
        <div className="flex justify-center gap-2 mt-4">
          {insights.map((_, idx) => (
            <div
              key={idx}
              className={`h-2 w-2 rounded-full transition-colors ${
                idx === currentIndex ? 'bg-blue-500' : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
```

### Alternative: Simpler Implementation

```typescript
// In your existing analyze handler
const handleAnalyze = async (username: string) => {
  setIsAnalyzing(true);
  
  // Start both requests in parallel
  const insightsPromise = fetch('/insights', {
    method: 'POST',
    headers: { 'X-API-Key': API_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({ username })
  }).then(r => r.json());
  
  const analysisPromise = fetch('/analyze', {
    method: 'POST',
    headers: { 'X-API-Key': API_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({ username })
  }).then(r => r.json());
  
  // Get insights quickly
  const { insights } = await insightsPromise;
  setRotatingInsights(insights);
  startRotation(); // Start 4-second rotation
  
  // Wait for main analysis
  const analysisData = await analysisPromise;
  setIsAnalyzing(false);
  setResults(analysisData);
};
```

## Key Benefits

1. **Better UX**: Users see interesting information immediately instead of staring at a spinner
2. **Perceived Performance**: Makes the wait feel shorter with engaging content
3. **Educational**: Users learn about their behavior patterns even before the full report
4. **Fast**: grok-3 is optimized for speed, so insights load quickly
5. **Smart Caching**: The context is cached, so `/insights` reuses data from `/analyze`

## Styling Recommendations

- Use fade transitions between insights (300-500ms)
- Keep text large and centered for readability
- Add subtle animation to draw attention
- Show progress dots to indicate how many insights are available
- Consider adding a "Skip to results" button for impatient users

## Error Handling

If `/insights` fails, fall back to generic messages:
- "Analyzing your activity patterns..."
- "Detecting interest signals..."
- "Mapping engagement behavior..."
- etc.

The fallback messages are built into the backend and will be returned automatically.
