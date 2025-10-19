"use client";

import { useState, useCallback, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sparkles, User, TrendingUp, MessageSquare } from "lucide-react";

// Common styling constants
const STYLES = {
  pageContainer: "min-h-screen bg-white py-20 px-4 sm:px-6 lg:px-8",
  mainHeading: "text-7xl font-black text-black tracking-tight",
  subHeading: "text-2xl text-gray-500 max-w-4xl mx-auto leading-relaxed font-light",
  card: "mb-16 shadow-2xl border border-gray-200 bg-white hover:shadow-3xl transition-all duration-500",
  cardHeader: "pb-8",
  cardTitle: "flex items-center gap-4 text-4xl font-bold text-black",
  cardDescription: "text-xl text-gray-600 leading-relaxed",
  input: "flex-1 h-16 text-xl border-2 border-gray-300 rounded-2xl transition-all duration-300 focus:border-black focus:ring-4 focus:ring-gray-200/50 focus:shadow-xl bg-gray-50",
  inputError: "border-red-500 focus:border-red-500 focus:ring-red-200",
  button: "w-full h-16 text-xl font-bold bg-black hover:bg-gray-800 text-white shadow-2xl hover:shadow-3xl transform hover:scale-[1.02] transition-all duration-300 rounded-2xl",
  errorCard: "mb-16 border border-red-300 bg-red-50 shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-500",
  resultsCard: "shadow-2xl border border-gray-200 bg-white hover:shadow-3xl transition-all duration-500",
  badge: "px-6 py-4 text-lg font-bold bg-gray-100 text-black border border-gray-300 hover:shadow-xl hover:scale-105 transition-all duration-300 rounded-full",
  recommendationsContent: "bg-gray-50 p-10 rounded-3xl border border-gray-300 shadow-inner",
  recommendationsText: "text-black whitespace-pre-wrap leading-relaxed text-2xl font-medium",
} as const;

interface AnalyzeResponse {
  topics: string[];
  recommendations: string;
}

export default function Home() {
  const [username, setUsername] = useState("");
  const [debouncedUsername, setDebouncedUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState("");
  const [inputError, setInputError] = useState("");

  // Debounce username input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedUsername(username);
    }, 500);

    return () => clearTimeout(timer);
  }, [username]);

  const validateUsername = (value: string): string => {
    if (!value.trim()) return "Username is required";
    if (value.length < 1 || value.length > 15) return "Username must be 1-15 characters";
    if (!/^[a-zA-Z0-9_]+$/.test(value)) return "Username can only contain letters, numbers, and underscores";
    return "";
  };

  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setUsername(value);
    setInputError(validateUsername(value));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validationError = validateUsername(debouncedUsername);
    if (validationError) {
      setInputError(validationError);
      return;
    }

    setLoading(true);
    setError("");
    setResults(null);

    try {
      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": "algo-x-demo-key-2025",
        },
        body: JSON.stringify({ username: debouncedUsername.trim() }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data: AnalyzeResponse = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={STYLES.pageContainer}>
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-20">
          <div className="flex items-center justify-center gap-6 mb-10">
            <div className="p-5 bg-black rounded-3xl shadow-2xl">
              <Sparkles className="w-12 h-12 text-white" />
            </div>
            <h1 className={STYLES.mainHeading}>
              X Algorithm Simulator
            </h1>
          </div>
          <p className={STYLES.subHeading}>
            Discover your personalized content recommendations based on Elon&apos;s Grok-powered algorithm
          </p>
        </div>

        <Card className={STYLES.card}>
          <CardHeader className={STYLES.cardHeader}>
            <CardTitle className={STYLES.cardTitle}>
              <div className="p-3 bg-gray-100 rounded-2xl">
                <User className="w-8 h-8 text-black" />
              </div>
              Enter Your X Username
            </CardTitle>
            <CardDescription className={STYLES.cardDescription}>
              We&apos;ll analyze your recent activity to show personalized topic recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-10">
              <div>
                <Input
                  type="text"
                  placeholder="e.g., elonmusk"
                  value={username}
                  onChange={handleUsernameChange}
                  className={`${STYLES.input} ${inputError ? STYLES.inputError : ''} hover:border-gray-400`}
                  disabled={loading}
                />
                {inputError && (
                  <p className="text-red-600 text-base mt-4 flex items-center gap-2 font-medium">
                    <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                    {inputError}
                  </p>
                )}
              </div>
              <Button
                type="submit"
                disabled={loading || !debouncedUsername.trim() || !!inputError}
                className={STYLES.button}
              >
                {loading ? (
                  <div className="flex items-center gap-4">
                    <div className="w-7 h-7 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-white font-semibold">Analyzing Your Profile...</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-3">
                    <TrendingUp className="w-7 h-7" />
                    Analyze Profile
                  </div>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {error && (
          <Card className={STYLES.errorCard}>
            <CardContent className="pt-10 pb-10">
              <p className="text-red-800 font-bold text-xl">{error}</p>
            </CardContent>
          </Card>
        )}

        {results && (
          <div className="space-y-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
            <Card className={STYLES.resultsCard}>
              <CardHeader className={STYLES.cardHeader}>
                <CardTitle className={STYLES.cardTitle}>
                  <div className="p-3 bg-gray-100 rounded-2xl">
                    <TrendingUp className="w-8 h-8 text-black" />
                  </div>
                  Your Interests
                </CardTitle>
                <CardDescription className={STYLES.cardDescription}>
                  Topics we&apos;ve identified from your X activity
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-5">
                  {results.topics.map((topic, index) => (
                    <Badge
                      key={index}
                      variant="secondary"
                      className={STYLES.badge}
                    >
                      {topic}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className={STYLES.resultsCard}>
              <CardHeader className={STYLES.cardHeader}>
                <CardTitle className={STYLES.cardTitle}>
                  <div className="p-3 bg-gray-100 rounded-2xl">
                    <MessageSquare className="w-8 h-8 text-black" />
                  </div>
                  Recommended Content
                </CardTitle>
                <CardDescription className={STYLES.cardDescription}>
                  Personalized recommendations from the algorithm
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className={STYLES.recommendationsContent}>
                  <p className={STYLES.recommendationsText}>
                    {results.recommendations}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
