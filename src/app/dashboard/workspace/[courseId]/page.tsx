"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useApp } from "@/context/AppContext";
import { 
  ArrowLeft, 
  Copy, 
  Download, 
  Save, 
  CheckCircle, 
  Layout, 
  Columns, 
  AlertCircle,
  HelpCircle,
  Sparkles,
  ChevronRight,
  Globe
} from "lucide-react";

export default function LocalizationWorkspace() {
  const router = useRouter();
  const params = useParams();
  const { courses, updateCourseTranslation } = useApp();
  
  // Find Course
  const courseId = params.courseId as string;
  const course = courses.find((c) => c.id === courseId);

  // States
  const [selectedTargetLang, setSelectedTargetLang] = useState("");
  const [activeBlockId, setActiveBlockId] = useState<number | null>(1);
  const [isSingleColumn, setIsSingleColumn] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  // Set default target lang once course is loaded
  useEffect(() => {
    if (course && course.targetLangs.length > 0 && !selectedTargetLang) {
      setSelectedTargetLang(course.targetLangs[0]);
    }
  }, [course, selectedTargetLang]);

  if (!course) {
    return (
      <div className="text-center py-20 space-y-4">
        <AlertCircle className="w-12 h-12 text-rose-500 mx-auto" />
        <h3 className="font-heading font-bold text-xl text-white">Course Not Found</h3>
        <p className="text-slate-400">The requested localization workspace does not exist or has been deleted.</p>
        <Link href="/dashboard/library" className="inline-flex items-center gap-2 text-accent-cyan hover:underline font-semibold">
          <ArrowLeft className="w-4 h-4" /> Return to Library
        </Link>
      </div>
    );
  }

  const sourceBlocks = course.sourceBlocks;
  const translatedBlocks = course.translatedBlocks[selectedTargetLang] || [];

  const handleTextareaChange = (blockId: number, text: string) => {
    updateCourseTranslation(courseId, selectedTargetLang, blockId, text);
  };

  const handleCopyAll = () => {
    const fullText = translatedBlocks.map((b) => b.text).join("\n\n");
    navigator.clipboard.writeText(fullText);
    alert("Copied all translations to clipboard!");
  };

  const handleSaveDraft = () => {
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };

  const handleApprovePublish = () => {
    alert(`Course "${course.title}" approved and compiled in ${selectedTargetLang}! Files synchronized to LMS.`);
    router.push("/dashboard/library");
  };

  // Find confidence rating of selected block
  const selectedBlockTranslation = translatedBlocks.find(b => b.id === activeBlockId);
  const currentConfidence = selectedBlockTranslation?.confidence || "Medium";

  const getConfidenceBadge = (confidence: "High" | "Medium" | "Low") => {
    switch (confidence) {
      case "High":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/25">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" /> High Confidence (90%+)
          </span>
        );
      case "Medium":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/25">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" /> Medium Confidence (70-90%)
          </span>
        );
      case "Low":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/25 animate-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400" /> Low Confidence (Under 70%)
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6 flex flex-col h-[calc(100vh-120px)]">
      
      {/* Workspace Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-bg-secondary p-5 rounded-2xl border border-border-custom">
        <div className="space-y-2 flex-1">
          <div className="flex items-center gap-2">
            <Link href="/dashboard/library" className="text-slate-400 hover:text-white p-1 hover:bg-white/5 rounded-lg transition-all">
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <h2 className="font-heading font-black text-xl text-white truncate max-w-sm sm:max-w-md md:max-w-lg lg:max-w-xl">
              {course.title}
            </h2>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-slate-400 font-bold uppercase tracking-wider">{course.contentType}</span>
            <span className="text-slate-600">•</span>
            <span className="bg-bg-primary border border-border-custom px-2.5 py-0.5 rounded-md font-semibold text-slate-300 flex items-center gap-1">
              {course.originalLang} 
              <ChevronRight className="w-3 h-3 text-slate-500" /> 
              {selectedTargetLang || "Loading..."}
            </span>
            <span className="text-slate-600">•</span>
            <span className="text-slate-400">AI Model: <span className="text-accent-cyan font-bold">{course.aiModel}</span></span>
          </div>
        </div>

        {/* Dynamic target language switcher */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400 font-semibold flex items-center gap-1">
            <Globe className="w-3.5 h-3.5" /> Language:
          </span>
          <div className="flex gap-1">
            {course.targetLangs.map((lang) => (
              <button
                key={lang}
                type="button"
                onClick={() => {
                  setSelectedTargetLang(lang);
                  setActiveBlockId(1);
                }}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                  selectedTargetLang === lang
                    ? "bg-accent-violet text-white glow-violet"
                    : "bg-bg-primary border border-border-custom hover:border-slate-500 text-slate-400 hover:text-white"
                }`}
              >
                {lang}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-bg-secondary/40 border border-border-custom p-3.5 rounded-xl">
        {/* Left Toolbar actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopyAll}
            className="px-3 py-2 rounded-lg border border-border-custom hover:border-slate-500 text-slate-300 hover:text-white text-xs font-semibold flex items-center gap-1.5 bg-bg-primary/40 transition-all"
          >
            <Copy className="w-3.5 h-3.5" /> Copy All
          </button>
          
          <button
            onClick={() => alert("Downloading formatted translation script as PDF...")}
            className="px-3 py-2 rounded-lg border border-border-custom hover:border-slate-500 text-slate-300 hover:text-white text-xs font-semibold flex items-center gap-1.5 bg-bg-primary/40 transition-all"
          >
            <Download className="w-3.5 h-3.5" /> Download PDF
          </button>
          
          <button
            onClick={handleSaveDraft}
            className="px-3 py-2 rounded-lg border border-border-custom hover:border-slate-500 text-slate-300 hover:text-white text-xs font-semibold flex items-center gap-1.5 bg-bg-primary/40 transition-all"
          >
            <Save className="w-3.5 h-3.5" /> {isSaved ? "Draft Saved!" : "Save Draft"}
          </button>
        </div>

        {/* Right Toolbar Actions */}
        <div className="flex items-center gap-3">
          {/* Column Toggle */}
          <button
            onClick={() => setIsSingleColumn(!isSingleColumn)}
            className="p-2 rounded-lg border border-border-custom hover:border-slate-500 text-slate-300 hover:text-white transition-all bg-bg-primary/40"
            title={isSingleColumn ? "Switch to side-by-side view" : "Switch to single-column view"}
          >
            {isSingleColumn ? <Columns className="w-4 h-4" /> : <Layout className="w-4 h-4" />}
          </button>

          <button
            onClick={handleApprovePublish}
            className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-xs flex items-center gap-1.5 transition-all glow-violet"
          >
            <CheckCircle className="w-4 h-4" /> Approve & Publish
          </button>
        </div>
      </div>

      {/* Main Content split scroll workspace container */}
      <div className="flex-1 min-h-0 overflow-hidden">
        <div className={`grid h-full gap-6 ${isSingleColumn ? "grid-cols-1 overflow-y-auto" : "grid-cols-2"}`}>
          
          {/* LEFT: SOURCE PANEL */}
          <div className={`flex flex-col h-full bg-bg-secondary border border-border-custom rounded-2xl overflow-hidden ${isSingleColumn ? "h-auto overflow-y-visible" : ""}`}>
            <div className="px-5 py-3 border-b border-border-custom bg-white/2 font-heading font-bold text-sm text-slate-300 flex items-center justify-between">
              <span>Source Transcript (English)</span>
              <span className="text-[10px] text-slate-500 font-mono uppercase">Original</span>
            </div>
            
            <div className={`flex-1 p-5 overflow-y-auto space-y-4 custom-scroll ${isSingleColumn ? "overflow-y-visible" : ""}`}>
              {sourceBlocks.map((block) => {
                const isActive = block.id === activeBlockId;
                return (
                  <div
                    key={block.id}
                    onClick={() => setActiveBlockId(block.id)}
                    className={`p-4 rounded-xl border transition-all cursor-pointer ${
                      isActive
                        ? "border-accent-violet/60 bg-accent-violet/5 text-white shadow-lg shadow-accent-violet/5"
                        : "border-border-custom/50 bg-white/2 text-slate-300 hover:border-slate-500/50"
                    }`}
                  >
                    <span className="text-[10px] text-accent-violet-light font-black tracking-wider block mb-1">
                      BLOCK {block.id.toString().padStart(2, "0")}
                    </span>
                    <p className="leading-relaxed text-sm">{block.text}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* RIGHT: TRANSLATED PANEL */}
          <div className={`flex flex-col h-full bg-bg-secondary border border-border-custom rounded-2xl overflow-hidden ${isSingleColumn ? "h-auto overflow-y-visible" : ""}`}>
            <div className="px-5 py-3 border-b border-border-custom bg-white/2 font-heading font-bold text-sm text-slate-300 flex items-center justify-between">
              <span>Translated Output ({selectedTargetLang})</span>
              <span className="text-[10px] text-accent-cyan font-bold uppercase tracking-wider flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-accent-cyan animate-pulse" /> AI Localized
              </span>
            </div>

            <div className={`flex-1 p-5 overflow-y-auto space-y-4 custom-scroll ${isSingleColumn ? "overflow-y-visible" : ""}`}>
              {translatedBlocks.map((block) => {
                const isActive = block.id === activeBlockId;
                return (
                  <div
                    key={block.id}
                    onClick={() => setActiveBlockId(block.id)}
                    className={`p-4 rounded-xl border transition-all ${
                      isActive
                        ? "border-accent-cyan/60 bg-accent-cyan/5 text-white shadow-lg shadow-accent-cyan/5"
                        : "border-border-custom/50 bg-white/2 text-slate-300 hover:border-slate-500/50"
                    }`}
                  >
                    <span className="text-[10px] text-accent-cyan font-black tracking-wider block mb-1">
                      BLOCK {block.id.toString().padStart(2, "0")}
                    </span>
                    <textarea
                      rows={3}
                      value={block.text}
                      onChange={(e) => handleTextareaChange(block.id, e.target.value)}
                      placeholder="Input translated content block..."
                      className="w-full bg-transparent border-0 p-0 text-sm text-white focus:ring-0 outline-none resize-none placeholder-slate-600 leading-relaxed"
                    />
                  </div>
                );
              })}
            </div>
          </div>

        </div>
      </div>

      {/* Bottom status bar */}
      <div className="bg-bg-secondary border border-border-custom p-4 rounded-xl flex items-center justify-between text-xs text-slate-400 shrink-0">
        <div className="flex items-center gap-3">
          <span>Active Selection: <span className="text-white font-bold">Block {activeBlockId?.toString().padStart(2, "0")}</span></span>
          <span className="text-slate-600">|</span>
          <div className="flex items-center gap-2">
            <span>AI Confidence Score:</span>
            {getConfidenceBadge(currentConfidence)}
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-2 font-mono text-[10px]">
          <span>Sync Scroller: <span className="text-emerald-400 font-bold">ACTIVE</span></span>
        </div>
      </div>
      
    </div>
  );
}
