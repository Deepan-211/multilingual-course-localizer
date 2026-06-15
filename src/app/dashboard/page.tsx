"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useApp, Course } from "@/context/AppContext";
import { 
  FileText, 
  Globe2, 
  CheckCircle2, 
  Clock, 
  ArrowUpRight, 
  Upload, 
  Settings as SettingsIcon, 
  Library,
  ChevronRight
} from "lucide-react";
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from "recharts";

const chartData = [
  { day: "Mon", translations: 2 },
  { day: "Tue", translations: 5 },
  { day: "Wed", translations: 3 },
  { day: "Thu", translations: 8 },
  { day: "Fri", translations: 12 },
  { day: "Sat", translations: 7 },
  { day: "Sun", translations: 15 },
];

export default function DashboardOverview() {
  const { courses } = useApp();
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Calculate dynamic stats
  const totalCourses = courses.length;
  
  const uniqueLanguagesSet = new Set<string>();
  courses.forEach(c => c.targetLangs.forEach(l => uniqueLanguagesSet.add(l)));
  const languagesProcessed = uniqueLanguagesSet.size;

  const completedLocalizations = courses.reduce((acc, c) => {
    // If completed, add number of targets
    if (c.status === "Completed") return acc + c.targetLangs.length;
    // Otherwise count target languages that actually have content
    let completedLangsCount = 0;
    Object.keys(c.translatedBlocks).forEach(lang => {
      const hasContent = c.translatedBlocks[lang].some(b => b.text !== "");
      if (hasContent) completedLangsCount++;
    });
    return acc + completedLangsCount;
  }, 0);

  const processingInQueue = courses.filter(c => c.status === "Processing" || c.status === "Queued").length;

  const getStatusBadge = (status: Course["status"]) => {
    switch (status) {
      case "Completed":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/25">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" /> Completed
          </span>
        );
      case "Processing":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/25 animate-status-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" /> Processing
          </span>
        );
      case "Failed":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/25">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400" /> Failed
          </span>
        );
      case "Queued":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/25">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-400" /> Queued
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-8">
      {/* Stat Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Stat 1 */}
        <div className="glass-panel rounded-2xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-accent-violet/30 to-transparent group-hover:from-accent-violet transition-all duration-300" />
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Courses Uploaded</span>
            <div className="w-10 h-10 rounded-xl bg-white/5 border border-border-custom flex items-center justify-center text-accent-violet-light">
              <FileText className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-black text-white">{totalCourses}</span>
          </div>
        </div>

        {/* Stat 2 */}
        <div className="glass-panel rounded-2xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-accent-cyan/30 to-transparent group-hover:from-accent-cyan transition-all duration-300" />
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Languages Processed</span>
            <div className="w-10 h-10 rounded-xl bg-white/5 border border-border-custom flex items-center justify-center text-accent-cyan">
              <Globe2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-black text-white">{languagesProcessed}</span>
          </div>
        </div>

        {/* Stat 3 */}
        <div className="glass-panel rounded-2xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-emerald-500/30 to-transparent group-hover:from-emerald-500 transition-all duration-300" />
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Localizations Completed</span>
            <div className="w-10 h-10 rounded-xl bg-white/5 border border-border-custom flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-black text-white">{completedLocalizations}</span>
          </div>
        </div>

        {/* Stat 4 */}
        <div className="glass-panel rounded-2xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-amber-500/30 to-transparent group-hover:from-amber-500 transition-all duration-300" />
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Processing In Queue</span>
            <div className="w-10 h-10 rounded-xl bg-white/5 border border-border-custom flex items-center justify-center text-amber-400 animate-status-pulse">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-black text-white">{processingInQueue}</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Chart & Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Columns: Localization Trend Chart & Recent Activity */}
        <div className="lg:col-span-2 space-y-8">
          {/* Chart Container */}
          <div className="glass-panel rounded-2xl p-6 border border-border-custom">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="font-heading font-bold text-lg text-white">Localization Activity</h3>
                <p className="text-xs text-slate-400">Total translations processed over the last 7 days</p>
              </div>
              <span className="text-xs font-semibold text-accent-cyan flex items-center gap-1">
                +18% this week <ArrowUpRight className="w-3.5 h-3.5" />
              </span>
            </div>
            
            <div className="h-64 w-full">
              {isMounted ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorTranslations" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#7C3AED" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#7C3AED" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2D3148" vertical={false} />
                    <XAxis dataKey="day" stroke="#94A3B8" fontSize={11} tickLine={false} />
                    <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: "#1A1D27", 
                        borderColor: "#2D3148",
                        borderRadius: "12px",
                        color: "#F8FAFC"
                      }} 
                    />
                    <Area 
                      type="monotone" 
                      dataKey="translations" 
                      stroke="#7C3AED" 
                      strokeWidth={2.5}
                      fillOpacity={1} 
                      fill="url(#colorTranslations)" 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="w-full h-full bg-white/5 rounded-xl animate-pulse flex items-center justify-center text-slate-500">
                  Loading charts...
                </div>
              )}
            </div>
          </div>

          {/* Recent Activity Table */}
          <div className="glass-panel rounded-2xl border border-border-custom overflow-hidden">
            <div className="px-6 py-5 border-b border-border-custom flex items-center justify-between">
              <div>
                <h3 className="font-heading font-bold text-lg text-white">Recent Activity</h3>
                <p className="text-xs text-slate-400">Manage recently uploaded and translated assets</p>
              </div>
              <Link href="/dashboard/library" className="text-xs text-accent-cyan hover:underline flex items-center gap-1 font-semibold">
                View Library <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="border-b border-border-custom bg-white/2">
                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">Course Name</th>
                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">Languages</th>
                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">Status</th>
                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">Date</th>
                    <th className="px-6 py-4 text-right"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-custom/50">
                  {courses.slice(0, 4).map((course) => (
                    <tr key={course.id} className="hover:bg-white/2 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-medium text-white max-w-[200px] sm:max-w-[300px] truncate">{course.title}</div>
                        <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold block mt-0.5">
                          {course.contentType}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-300">
                        <div className="flex flex-wrap gap-1 max-w-[150px]">
                          {course.targetLangs.map((lang, lIdx) => (
                            <span 
                              key={lIdx} 
                              className="text-xs bg-bg-primary/80 border border-border-custom px-2 py-0.5 rounded-md font-medium"
                            >
                              {lang}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4">{getStatusBadge(course.status)}</td>
                      <td className="px-6 py-4 text-slate-400 font-mono text-xs">{course.date}</td>
                      <td className="px-6 py-4 text-right">
                        {course.status === "Completed" ? (
                          <Link 
                            href={`/dashboard/workspace/${course.id}`}
                            className="inline-flex items-center gap-1 text-xs font-bold text-accent-violet-light hover:text-white transition-colors"
                          >
                            Open <ChevronRight className="w-3.5 h-3.5" />
                          </Link>
                        ) : course.status === "Processing" ? (
                          <Link 
                            href="/dashboard/progress"
                            className="inline-flex items-center gap-1 text-xs font-bold text-accent-cyan hover:text-white transition-colors"
                          >
                            Monitor <ChevronRight className="w-3.5 h-3.5" />
                          </Link>
                        ) : (
                          <span className="text-xs text-slate-500 cursor-not-allowed">Locked</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right 1 Column: Quick Actions & System Info */}
        <div className="space-y-8">
          {/* Quick Actions Panel */}
          <div className="glass-panel rounded-2xl p-6 border border-border-custom">
            <h3 className="font-heading font-bold text-lg text-white mb-4">Quick Actions</h3>
            <div className="space-y-4">
              <Link 
                href="/dashboard/upload" 
                className="w-full flex items-center justify-between p-4 rounded-xl border border-border-custom bg-white/2 hover:bg-accent-violet/5 hover:border-accent-violet/40 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-accent-violet/10 border border-accent-violet/25 flex items-center justify-center text-accent-violet-light group-hover:scale-105 transition-transform">
                    <Upload className="w-5 h-5" />
                  </div>
                  <div className="text-left">
                    <span className="text-sm font-semibold text-white block">Upload New Course</span>
                    <span className="text-[10px] text-slate-500 block">Videos, transcripts, PDFs</span>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-white transition-colors" />
              </Link>

              <Link 
                href="/dashboard/library" 
                className="w-full flex items-center justify-between p-4 rounded-xl border border-border-custom bg-white/2 hover:bg-accent-cyan/5 hover:border-accent-cyan/40 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-accent-cyan/10 border border-accent-cyan/25 flex items-center justify-center text-accent-cyan group-hover:scale-105 transition-transform">
                    <Library className="w-5 h-5" />
                  </div>
                  <div className="text-left">
                    <span className="text-sm font-semibold text-white block">View Course Library</span>
                    <span className="text-[10px] text-slate-500 block">Manage localization catalog</span>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-white transition-colors" />
              </Link>

              <Link 
                href="/dashboard/settings" 
                className="w-full flex items-center justify-between p-4 rounded-xl border border-border-custom bg-white/2 hover:bg-white/5 hover:border-slate-500 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-white/5 border border-border-custom flex items-center justify-center text-slate-400 group-hover:scale-105 transition-transform">
                    <SettingsIcon className="w-5 h-5" />
                  </div>
                  <div className="text-left">
                    <span className="text-sm font-semibold text-white block">Configure Settings</span>
                    <span className="text-[10px] text-slate-500 block">Configure models, engines</span>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-white transition-colors" />
              </Link>
            </div>
          </div>

          {/* Mini System Info Panel */}
          <div className="glass-panel rounded-2xl p-6 border border-border-custom text-slate-400 text-xs">
            <h4 className="font-heading font-bold text-sm text-white mb-3 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> System Health
            </h4>
            <div className="space-y-3 font-mono">
              <div className="flex justify-between">
                <span>GPU Cluster Load:</span>
                <span className="text-emerald-400 font-semibold">14.5%</span>
              </div>
              <div className="flex justify-between">
                <span>Translation API:</span>
                <span className="text-emerald-400 font-semibold">Online (99.98%)</span>
              </div>
              <div className="flex justify-between">
                <span>Worker Threads:</span>
                <span className="text-white">32/32 Idle</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
