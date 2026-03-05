"use client";

import { useState } from "react";

export default function DashboardPage() {
  const [symbol, setSymbol] = useState("AAPL");

  return (
    <main style={{ padding: 24 }}>
      <h2>Dashboard</h2>
      <label>
        Symbol
        <input value={symbol} onChange={(e) => setSymbol(e.target.value)} style={{ marginLeft: 8 }} />
      </label>
      <p>Use backend endpoints `/market/{symbol}`, `/analyze-chart`, and `/trade-plan` from this page.</p>
    </main>
  );
}
