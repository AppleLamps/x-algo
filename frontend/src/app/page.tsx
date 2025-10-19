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
  button: "w-full min-h-16 py-4 text-xl font-bold bg-black hover:bg-gray-800 text-white shadow-2xl hover:shadow-3xl transform hover:scale-[1.02] transition-all duration-300 rounded-2xl",
  errorCard: "mb-16 border border-red-300 bg-red-50 shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-500",
  resultsCard: "shadow-2xl border border-gray-200 bg-white hover:shadow-3xl transition-all duration-500",
  badge: "px-6 py-4 text-lg font-bold bg-gray-100 text-black border border-gray-300 hover:shadow-xl hover:scale-105 transition-all duration-300 rounded-full",
  recommendationsContent: "bg-gray-50 p-10 rounded-3xl border border-gray-300 shadow-inner",
  recommendationsText: "text-black whitespace-pre-wrap leading-relaxed text-2xl font-medium",
} as const;

interface TopicWithWeight {
  topic: string;
  weight: number;
}

interface Signal {
  name: string;
  adjustment: string;
  reason: string;
}

interface FeedComposition {
  increase: string[];
  decrease: string[];
  account_distribution: string;
}

interface QualityMetrics {
  prioritized_signals: string[];
  spam_filters: string[];
  diversity_mechanisms: string[];
}

interface AlgorithmReport {
  analysis_process: string;
  signals_boosted: Signal[];
  signals_reduced: Signal[];
  feed_composition: FeedComposition;
  quality_metrics: QualityMetrics;
  expected_outcome: string;
}

interface AnalyzeResponse {
  topics: TopicWithWeight[];
  recommendations: {
    report: AlgorithmReport;
    tokens: {
      completion_tokens: number;
      reasoning_tokens: number;
      total_tokens: number;
    };
  };
}

export default function Home() {
  const [username, setUsername] = useState("");
  const [debouncedUsername, setDebouncedUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState("");
  const [inputError, setInputError] = useState("");
  const [insights, setInsights] = useState<string[]>([]);
  const [currentInsightIndex, setCurrentInsightIndex] = useState(0);

  // Debounce username input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedUsername(username);
    }, 500);

    return () => clearTimeout(timer);
  }, [username]);

  // Rotate insights every 4 seconds while loading
  useEffect(() => {
    if (!loading || insights.length === 0) return;

    const interval = setInterval(() => {
      setCurrentInsightIndex((prev) => (prev + 1) % insights.length);
    }, 4000);

    return () => clearInterval(interval);
  }, [loading, insights.length]);

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
    setInsights([]);
    setCurrentInsightIndex(0);

    try {
      const trimmedUsername = debouncedUsername.trim();
      const apiKey = "algo-x-demo-key-2025";
      const headers = {
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
      };

      // Start both requests in parallel
      const insightsPromise = fetch("http://localhost:8000/insights", {
        method: "POST",
        headers,
        body: JSON.stringify({ username: trimmedUsername }),
      }).then(res => res.json()).catch(() => ({ insights: ["Analyzing your profile..."] }));

      const analyzePromise = fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers,
        body: JSON.stringify({ username: trimmedUsername }),
      });

      // Get insights quickly
      const insightsData = await insightsPromise;
      setInsights(insightsData.insights || ["Analyzing your profile..."]);

      // Wait for main analysis
      const response = await analyzePromise;
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
                  <div className="flex flex-col items-center gap-3 w-full">
                    <div className="flex items-center gap-4">
                      <div className="w-7 h-7 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-white font-semibold">Analyzing Your Profile</span>
                    </div>
                    {insights.length > 0 && (
                      <div className="text-sm text-white/90 text-center transition-opacity duration-500 animate-pulse">
                        {insights[currentInsightIndex]}
                      </div>
                    )}
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
                  {results.topics.map((topicItem, index) => (
                    <Badge
                      key={index}
                      variant="secondary"
                      className={STYLES.badge}
                      style={{
                        opacity: 0.4 + (topicItem.weight * 0.6)
                      }}
                      title={`Weight: ${(topicItem.weight * 100).toFixed(0)}%`}
                    >
                      {topicItem.topic}
                      <span className="ml-2 text-sm opacity-70">
                        {(topicItem.weight * 100).toFixed(0)}%
                      </span>
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
                  Algorithm Adjustment Report
                </CardTitle>
                <CardDescription className={STYLES.cardDescription}>
                  Technical analysis of how the algorithm will adjust for your profile
                  <span className="ml-2 text-sm opacity-60">
                    ({results.recommendations.tokens.reasoning_tokens} reasoning tokens, {results.recommendations.tokens.completion_tokens} completion tokens)
                  </span>
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-8">
                  {/* Analysis Process */}
                  <div className="bg-blue-50 p-6 rounded-xl border border-blue-200">
                    <h3 className="text-xl font-bold text-blue-900 mb-3">Analysis Process</h3>
                    <p className="text-blue-800 leading-relaxed">{results.recommendations.report.analysis_process}</p>
                  </div>

                  {/* Signals Boosted */}
                  <div className="bg-green-50 p-6 rounded-xl border border-green-200">
                    <h3 className="text-xl font-bold text-green-900 mb-4">Signals Being Boosted</h3>
                    <div className="space-y-3">
                      {results.recommendations.report.signals_boosted.map((signal, idx) => (
                        <div key={idx} className="bg-white p-4 rounded-lg border border-green-300">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="font-bold text-green-700 text-lg">{signal.name}</span>
                            <Badge className="bg-green-600 text-white">{signal.adjustment}</Badge>
                          </div>
                          <p className="text-gray-700 text-sm">{signal.reason}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Signals Reduced */}
                  <div className="bg-red-50 p-6 rounded-xl border border-red-200">
                    <h3 className="text-xl font-bold text-red-900 mb-4">Signals Being Reduced</h3>
                    <div className="space-y-3">
                      {results.recommendations.report.signals_reduced.map((signal, idx) => (
                        <div key={idx} className="bg-white p-4 rounded-lg border border-red-300">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="font-bold text-red-700 text-lg">{signal.name}</span>
                            <Badge className="bg-red-600 text-white">{signal.adjustment}</Badge>
                          </div>
                          <p className="text-gray-700 text-sm">{signal.reason}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Feed Composition */}
                  <div className="bg-purple-50 p-6 rounded-xl border border-purple-200">
                    <h3 className="text-xl font-bold text-purple-900 mb-4">Feed Composition Changes</h3>
                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <h4 className="font-semibold text-purple-800 mb-2">Increasing ↑</h4>
                        <ul className="list-disc list-inside space-y-1 text-purple-700">
                          {results.recommendations.report.feed_composition.increase.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-semibold text-purple-800 mb-2">Decreasing ↓</h4>
                        <ul className="list-disc list-inside space-y-1 text-purple-700">
                          {results.recommendations.report.feed_composition.decrease.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    <div className="bg-white p-4 rounded-lg border border-purple-300">
                      <span className="font-semibold text-purple-800">Account Distribution: </span>
                      <span className="text-purple-700">{results.recommendations.report.feed_composition.account_distribution}</span>
                    </div>
                  </div>

                  {/* Quality Metrics */}
                  <div className="bg-orange-50 p-6 rounded-xl border border-orange-200">
                    <h3 className="text-xl font-bold text-orange-900 mb-4">Quality Metrics Applied</h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold text-orange-800 mb-2">Prioritized Signals</h4>
                        <div className="flex flex-wrap gap-2">
                          {results.recommendations.report.quality_metrics.prioritized_signals.map((sig, idx) => (
                            <Badge key={idx} className="bg-orange-200 text-orange-900">{sig}</Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-semibold text-orange-800 mb-2">Spam Filters</h4>
                        <div className="flex flex-wrap gap-2">
                          {results.recommendations.report.quality_metrics.spam_filters.map((filter, idx) => (
                            <Badge key={idx} className="bg-orange-300 text-orange-900">{filter}</Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-semibold text-orange-800 mb-2">Diversity Mechanisms</h4>
                        <div className="flex flex-wrap gap-2">
                          {results.recommendations.report.quality_metrics.diversity_mechanisms.map((mech, idx) => (
                            <Badge key={idx} className="bg-orange-400 text-white">{mech}</Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Expected Outcome */}
                  <div className="bg-gray-100 p-6 rounded-xl border border-gray-300">
                    <h3 className="text-xl font-bold text-gray-900 mb-3">Expected Outcome</h3>
                    <p className="text-gray-800 leading-relaxed text-lg">{results.recommendations.report.expected_outcome}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
