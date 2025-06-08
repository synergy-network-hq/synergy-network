import React from "react";

export default function RewardsPanel({ rewards }) {
  return (
    <div className="bg-white/10 rounded-2xl p-8 shadow-lg glassmorphism flex flex-col justify-between min-w-[230px]">
      <div>
        <div className="text-xl font-semibold text-blue-200 mb-2">Rewards</div>
        <div className="flex flex-col gap-1">
          <span>
            Last payout: <span className="text-green-200 font-bold">{rewards.lastPayout}</span>
          </span>
          <span>
            Next payout: <span className="text-blue-100">{rewards.nextPayout}</span>
          </span>
          <span>
            Expected: <span className="text-blue-300">{rewards.expected}</span>
          </span>
        </div>
      </div>
      <button className="mt-6 py-2 bg-blue-600 rounded-xl text-white font-medium shadow hover:bg-blue-500 transition">
        View Payout History
      </button>
    </div>
  );
}
