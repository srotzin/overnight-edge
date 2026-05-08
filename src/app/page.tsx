import Image from "next/image";

export default function Home() {
  return (
    <main className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero */}
      <section className="flex flex-col items-center justify-center px-4 py-24 text-center">
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
          Overnight Edge
        </h1>
        <p className="text-lg md:text-xl text-gray-400 max-w-2xl">
          AI-generated market intelligence. Zero humans. Delivered to your Telegram before the market opens.
        </p>
      </section>

      {/* Cards */}
      <section className="px-4 py-12 max-w-5xl mx-auto grid md:grid-cols-2 gap-8">
        {/* Card 1 */}
        <div className="border border-gray-800 rounded-2xl p-8 hover:border-[#00c853] transition-colors">
          <h2 className="text-2xl font-bold mb-2">Daily Brief</h2>
          <p className="text-[#00c853] text-xl font-semibold mb-6">$49/mo</p>
          <ul className="space-y-3 text-gray-400 mb-8 text-left">
            <li>Pre-market brief every trading day 8:00 AM EST</li>
            <li>S&P 500/Nasdaq futures, VIX, gainers/losers</li>
            <li>Earnings, economic data, breaking news</li>
          </ul>
          <a
            href="https://buy.stripe.com/prod_UTd168i0Iw8b3M"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block w-full text-center bg-[#00c853] text-black font-semibold py-3 rounded-lg hover:bg-[#00b34a] transition-colors"
          >
            Subscribe
          </a>
        </div>

        {/* Card 2 */}
        <div className="border border-gray-800 rounded-2xl p-8 hover:border-[#00c853] transition-colors">
          <h2 className="text-2xl font-bold mb-2">SignalSynthesizer</h2>
          <p className="text-[#00c853] text-xl font-semibold mb-6">$149/mo</p>
          <ul className="space-y-3 text-gray-400 mb-8 text-left">
            <li>Everything in Daily Brief, plus:</li>
            <li>Congressional trade alerts (STOCK Act)</li>
            <li>Insider filings (SEC Form 4)</li>
            <li>Unusual options flow, dark pool prints</li>
            <li>Confluence scoring 3/5 minimum to alert</li>
            <li>Real-time delivery</li>
          </ul>
          <a
            href="https://buy.stripe.com/prod_UTd2L2yQEam5Cl"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block w-full text-center bg-[#00c853] text-black font-semibold py-3 rounded-lg hover:bg-[#00b34a] transition-colors"
          >
            Subscribe
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-4 py-12 text-center text-gray-600 text-sm">
        <p>Fully automated by KimiClaw AI. Cancel anytime in Stripe. Not financial advice.</p>
      </footer>
    </main>
  );
}
