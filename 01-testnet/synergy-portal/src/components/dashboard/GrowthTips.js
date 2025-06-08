import React from "react";

export default function GrowthTips({ tips = [] }) {
  return (
    <div className="bg-white/10 rounded-2xl p-6 shadow-lg glassmorphism min-w-[230px] flex flex-col justify-between">
      <div>
        <div className="text-lg font-semibold text-blue-200 mb-2">Next Steps</div>
        <ul className="text-blue-100 list-disc list-inside space-y-1">
          {tips.map((tip, i) => (
            <li key={i}>{tip}</li>
          ))}
        </ul>
      </div>
      <button className="mt-6 py-2 bg-blue-600 rounded-xl text-white font-medium shadow hover:bg-blue-500 transition">
        Explore More Ways to Earn
      </button>
    </div>
  );
}
