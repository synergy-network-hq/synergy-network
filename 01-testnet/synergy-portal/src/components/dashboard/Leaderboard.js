import React from "react";

export default function Leaderboard({ leaderboard = [] }) {
  return (
    <div className="bg-white/10 rounded-2xl p-6 shadow-lg glassmorphism min-w-[260px]">
      <div className="text-lg font-semibold text-blue-200 mb-3">Leaderboard (Top 5)</div>
      <ol className="list-decimal list-inside text-blue-100 space-y-1">
        {leaderboard.map((l, i) => (
          <li key={l.name} className={`${l.name === "You" ? "font-bold text-blue-300" : ""}`}>
            {l.name} <span className="text-blue-300 font-medium">{l.score}</span>
            <span className="text-xs text-gray-400 ml-2">({l.cluster})</span>
          </li>
        ))}
      </ol>
      <button className="mt-4 w-full py-2 bg-blue-700 rounded-xl text-white font-medium shadow hover:bg-blue-600 transition">
        See Full Leaderboard
      </button>
    </div>
  );
}
