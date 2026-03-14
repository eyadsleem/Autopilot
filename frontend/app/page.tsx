import Link from "next/link";

export default function HomePage() {
  return (
    <main style={{ padding: 24 }}>
      <h1>SnapTrader Decision Support</h1>
      <p>Sign in, upload charts, and review AI-generated trade plans.</p>
      <Link href="/dashboard">Go to dashboard</Link>
    </main>
  );
}
