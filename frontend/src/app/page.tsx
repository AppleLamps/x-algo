"use client";

import React, { useState, useCallback, useEffect } from "react";
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

interface DiversityMetrics {
  diversity_score: number;
  topic_entropy: number;
  filter_bubble_risk: string;
  viewpoint_diversity: string;
}

interface OpposingViewpoints {
  included: boolean;
  topics_with_diversity: string[];
  explanation: string;
}

interface TemporalAnalysis {
  recency_bias: string;
  temporal_mix_explanation: string;
  content_freshness: string;
}

interface RecommendationExplanation {
  signal_name: string;
  why_this_recommendation: string;
  expected_impact: string;
}

interface AlgorithmReport {
  analysis_process: string;
  signals_boosted: Signal[];
  signals_reduced: Signal[];
  feed_composition: FeedComposition;
  quality_metrics: QualityMetrics;
  diversity_metrics: DiversityMetrics;
  opposing_viewpoints: OpposingViewpoints;
  temporal_analysis: TemporalAnalysis;
  recommendation_explanations: RecommendationExplanation[];
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

// Helper component for progress bar with dynamic width (using ref to avoid inline styles warning)
const ProgressBar = ({ percentage, colorClass }: { percentage: number; colorClass: string }) => {
  const ref = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (ref.current) {
      ref.current.style.setProperty('--progress-width', `${percentage}%`);
    }
  }, [percentage]);

  return (
    <div ref={ref} className={`h-2 rounded-full transition-all progress-bar ${colorClass}`}></div>
  );
};

// Helper component for weighted badge with dynamic opacity (using ref to avoid inline styles warning)
const WeightedBadge = ({ topic, weight, className }: { topic: string; weight: number; className: string }) => {
  const ref = React.useRef<HTMLSpanElement>(null);

  React.useEffect(() => {
    if (ref.current) {
      ref.current.style.setProperty('--badge-opacity', String(0.4 + (weight * 0.6)));
    }
  }, [weight]);

  return (
    <Badge
      ref={ref}
      variant="secondary"
      className={`${className} weighted-badge`}
      title={`Weight: ${(weight * 100).toFixed(0)}%`}
    >
      {topic}
      <span className="ml-2 text-sm opacity-70">
        {(weight * 100).toFixed(0)}%
      </span>
    </Badge>
  );
};

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
                    <WeightedBadge
                      key={index}
                      topic={topicItem.topic}
                      weight={topicItem.weight}
                      className={STYLES.badge}
                    />
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

                  {/* Diversity Score & Filter Bubble Risk */}
                  <div className="bg-indigo-50 p-6 rounded-xl border border-indigo-200">
                    <h3 className="text-xl font-bold text-indigo-900 mb-4">🎯 Feed Diversity Assessment</h3>
                    <div className="grid md:grid-cols-2 gap-6">
                      <div className="bg-white p-4 rounded-lg border border-indigo-300">
                        <div className="flex items-end gap-2 mb-2">
                          <span className="text-3xl font-bold text-indigo-700">
                            {results.recommendations.report.diversity_metrics.diversity_score.toFixed(0)}
                          </span>
                          <span className="text-indigo-600 font-semibold mb-1">/100</span>
                        </div>
                        <p className="text-sm text-indigo-800 font-semibold">Diversity Score</p>
                        <p className="text-xs text-indigo-600 mt-2">Higher scores indicate more topic variety in your feed</p>

                        {/* Visual progress bar - uses helper component */}
                        <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
                          <ProgressBar
                            percentage={results.recommendations.report.diversity_metrics.diversity_score}
                            colorClass={
                              results.recommendations.report.diversity_metrics.diversity_score > 70 ? 'bg-green-500' :
                                results.recommendations.report.diversity_metrics.diversity_score > 50 ? 'bg-yellow-500' :
                                  'bg-red-500'
                            }
                          />
                        </div>
                      </div>

                      <div className="bg-white p-4 rounded-lg border border-indigo-300">
                        <div className="mb-3">
                          <p className="text-sm text-indigo-800 font-semibold mb-1">Filter Bubble Risk</p>
                          <Badge className={`${results.recommendations.report.diversity_metrics.filter_bubble_risk === 'Low' ? 'bg-green-600' :
                            results.recommendations.report.diversity_metrics.filter_bubble_risk === 'Moderate' ? 'bg-yellow-600' :
                              'bg-red-600'
                            } text-white text-sm py-2 px-3`}>
                            {results.recommendations.report.diversity_metrics.filter_bubble_risk}
                          </Badge>
                          <p className="text-xs text-indigo-600 mt-2">Risk of algorithm creating an echo chamber</p>
                        </div>
                        <div className="text-sm text-indigo-700 mt-3 p-3 bg-indigo-100 rounded">
                          <p className="font-semibold mb-1">Topic Entropy: {(results.recommendations.report.diversity_metrics.topic_entropy * 100).toFixed(0)}%</p>
                          <p className="text-xs">Measures how spread out your interests are across different topics</p>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 bg-white p-4 rounded-lg border border-indigo-300">
                      <p className="text-sm font-semibold text-indigo-900 mb-2">Viewpoint Diversity</p>
                      <p className="text-indigo-700 text-sm leading-relaxed">{results.recommendations.report.diversity_metrics.viewpoint_diversity}</p>
                    </div>
                  </div>

                  {/* Opposing Viewpoints */}
                  {results.recommendations.report.opposing_viewpoints.included && (
                    <div className="bg-emerald-50 p-6 rounded-xl border border-emerald-200">
                      <h3 className="text-xl font-bold text-emerald-900 mb-4">🔄 Opposing Viewpoints Strategy</h3>
                      <div className="space-y-3">
                        <div>
                          <p className="text-sm font-semibold text-emerald-800 mb-2">Topics with Diverse Perspectives:</p>
                          <div className="flex flex-wrap gap-2">
                            {results.recommendations.report.opposing_viewpoints.topics_with_diversity.map((topic, idx) => (
                              <Badge key={idx} className="bg-emerald-200 text-emerald-900">{topic}</Badge>
                            ))}
                          </div>
                        </div>
                        <div className="bg-white p-4 rounded-lg border border-emerald-300">
                          <p className="text-emerald-700 text-sm leading-relaxed">{results.recommendations.report.opposing_viewpoints.explanation}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Temporal Analysis */}
                  <div className="bg-sky-50 p-6 rounded-xl border border-sky-200">
                    <h3 className="text-xl font-bold text-sky-900 mb-4">⏱️ Temporal Content Mix</h3>
                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div className="bg-white p-4 rounded-lg border border-sky-300">
                        <p className="text-sm font-semibold text-sky-800 mb-2">Recency Bias</p>
                        <p className="text-sky-700 font-semibold">{results.recommendations.report.temporal_analysis.recency_bias}</p>
                        <p className="text-xs text-sky-600 mt-2">How recent vs. timeless your content is</p>
                      </div>
                      <div className="bg-white p-4 rounded-lg border border-sky-300">
                        <p className="text-sm font-semibold text-sky-800 mb-2">Content Freshness</p>
                        <p className="text-sky-700 font-semibold">{results.recommendations.report.temporal_analysis.content_freshness}</p>
                        <p className="text-xs text-sky-600 mt-2">Distribution of recent vs. evergreen content</p>
                      </div>
                    </div>
                    <div className="bg-white p-4 rounded-lg border border-sky-300">
                      <p className="text-sky-700 text-sm leading-relaxed">{results.recommendations.report.temporal_analysis.temporal_mix_explanation}</p>
                    </div>
                  </div>

                  {/* Why This Recommendation */}
                  {results.recommendations.report.recommendation_explanations.length > 0 && (
                    <div className="bg-fuchsia-50 p-6 rounded-xl border border-fuchsia-200">
                      <h3 className="text-xl font-bold text-fuchsia-900 mb-4">💡 Why These Recommendations?</h3>
                      <div className="space-y-3">
                        {results.recommendations.report.recommendation_explanations.map((exp, idx) => (
                          <div key={idx} className="bg-white p-4 rounded-lg border border-fuchsia-300">
                            <div className="flex items-start gap-3">
                              <div className="flex-1">
                                <p className="font-semibold text-fuchsia-900 mb-1">{exp.signal_name}</p>
                                <p className="text-fuchsia-700 text-sm mb-2">{exp.why_this_recommendation}</p>
                                <div className="bg-fuchsia-100 p-3 rounded border border-fuchsia-200">
                                  <p className="text-xs font-semibold text-fuchsia-800 mb-1">What you'll notice:</p>
                                  <p className="text-xs text-fuchsia-700">{exp.expected_impact}</p>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

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
