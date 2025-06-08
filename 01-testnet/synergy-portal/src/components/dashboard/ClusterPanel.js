import React from "react";

export default function ClusterPanel({ clusters = [] }) {
  return (
    <div className="bg-white/10 rounded-2xl p-6 shadow-lg glassmorphism">
      <div className="text-lg font-semibold text-blue-200 mb-3">Your Clusters</div>
      <ul>
        {clusters.map((c, i) => (
          <li key={c.name} className="flex justify-between items-center py-1">
            <span className="text-blue-100 font-medium">{c.name}</span>
            <span className="text-blue-300">{c.synergy} synergy</span>
            <button className="ml-2 text-xs bg-blue-700 hover:bg-blue-800 px-2 py-1 rounded text-white shadow">
              View
            </button>
          </li>
        ))}
      </ul>
      <button className="mt-4 w-full py-2 bg-blue-700 rounded-xl text-white font-medium shadow hover:bg-blue-600 transition">
        Join or Create Cluster
      </button>
    </div>
  );
}
