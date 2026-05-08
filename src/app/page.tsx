export default function Home() {
  return (
    <main className="min-h-screen bg-[#0a0a0a] text-white px-6 py-16 relative overflow-hidden">
      {/* Green Tesla sparks background */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/4 w-1 h-1 bg-[#00c853] rounded-full animate-pulse shadow-[0_0_10px_#00c853]" />
        <div className="absolute top-20 right-1/3 w-2 h-2 bg-[#00c853] rounded-full animate-ping opacity-60" />
        <div className="absolute top-40 left-1/2 w-1 h-1 bg-[#00ff6a] rounded-full animate-pulse shadow-[0_0_15px_#00ff6a]" />
        <div className="absolute top-60 right-1/4 w-1 h-1 bg-[#00c853] rounded-full animate-pulse shadow-[0_0_8px_#00c853]" />
        <div className="absolute bottom-40 left-1/3 w-2 h-2 bg-[#00ff6a] rounded-full animate-ping opacity-40" />
        <div className="absolute bottom-20 right-1/2 w-1 h-1 bg-[#00c853] rounded-full animate-pulse shadow-[0_0_12px_#00c853]" />
        <div className="absolute top-1/3 left-10 w-px h-20 bg-gradient-to-b from-transparent via-[#00c853] to-transparent opacity-30" />
        <div className="absolute top-1/2 right-20 w-px h-32 bg-gradient-to-b from-transparent via-[#00ff6a] to-transparent opacity-20" />
        <div className="absolute bottom-1/3 left-1/4 w-px h-16 bg-gradient-to-b from-transparent via-[#00c853] to-transparent opacity-25" />
      </div>

      <div className="max-w-6xl mx-auto relative z-10">
        {/* Hero with logo */}
        <div className="text-center mb-20">
          <img
            src="/cartoons/overnight_logo_bot.png"
            alt="OverNight Edge Bot"
            className="mx-auto mb-8 w-48 h-48 object-contain drop-shadow-[0_0_30px_rgba(0,200,83,0.3)]"
          />
          <h1 className="text-5xl md:text-7xl font-bold mb-6 tracking-tight">
            Overnight Edge
          </h1>
          <p className="text-xl md:text-2xl text-gray-400 max-w-2xl mx-auto">
            AI-powered market intelligence. Zero humans. Delivered to your Telegram.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1 — Daily Digest */}
          <div className="border border-gray-800 rounded-2xl p-8 hover:border-[#00c853] transition-colors">
            <div className="text-[#00c853] text-sm font-semibold mb-2">TIER 1</div>
            <h2 className="text-2xl font-bold mb-2">Daily Digest</h2>
            <div className="text-4xl font-bold mb-6">$49<span className="text-lg text-gray-400">/mo</span></div>
            <ul className="space-y-3 text-gray-300 mb-8 text-sm">
              <li>Pre-market brief every trading day 8:00 AM EST</li>
              <li>S&P 500 / Nasdaq futures</li>
              <li>VIX, gainers/losers</li>
              <li>Earnings, economic data</li>
              <li>Breaking news with sentiment</li>
            </ul>
            <a
              href="https://buy.stripe.com/test_prod_UTd168i0Iw8b3M"
              className="block w-full text-center bg-white text-black font-semibold py-3 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Subscribe
            </a>
          </div>

          {/* Card 2 — Signal Synthesizer */}
          <div className="border border-gray-800 rounded-2xl p-8 hover:border-[#00c853] transition-colors">
            <div className="text-[#00c853] text-sm font-semibold mb-2">TIER 2</div>
            <h2 className="text-2xl font-bold mb-2">Signal Synthesizer</h2>
            <div className="text-4xl font-bold mb-6">$149<span className="text-lg text-gray-400">/mo</span></div>
            <ul className="space-y-3 text-gray-300 mb-8 text-sm">
              <li>Everything in Daily Digest</li>
              <li>Congressional trade alerts (STOCK Act)</li>
              <li>Insider filings (SEC Form 4)</li>
              <li>Unusual options flow</li>
              <li>Dark pool prints</li>
              <li>Confluence scoring 3/5 minimum</li>
            </ul>
            <a
              href="https://buy.stripe.com/test_prod_UTd2L2yQEam5Cl"
              className="block w-full text-center bg-white text-black font-semibold py-3 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Subscribe
            </a>
          </div>

          {/* Card 3 — Short Squeeze Radar */}
          <div className="border border-gray-800 rounded-2xl p-8 hover:border-[#00c853] transition-colors">
            <div className="text-[#00c853] text-sm font-semibold mb-2">STANDALONE</div>
            <h2 className="text-2xl font-bold mb-2">Short Squeeze Radar</h2>
            <div className="text-4xl font-bold mb-6">$99<span className="text-lg text-gray-400">/mo</span></div>
            <ul className="space-y-3 text-gray-300 mb-8 text-sm">
              <li>Twice daily: 6:30 AM + 12:30 PM EST</li>
              <li>Short interest &gt;20% of float scan</li>
              <li>Low float + high days-to-cover</li>
              <li>Options gamma ramp detection</li>
              <li>Squeeze Score 1-10 (alerts on 6+)</li>
              <li>Social volume & borrow utilization</li>
            </ul>
            <a
              href="https://buy.stripe.com/test_prod_UTnEW457mr8e8Y"
              className="block w-full text-center bg-white text-black font-semibold py-3 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Subscribe
            </a>
          </div>

          {/* Card 4 — X10 Signal */}
          <div className="border border-gray-800 rounded-2xl p-8 hover:border-[#00c853] transition-colors">
            <div className="text-[#00c853] text-sm font-semibold mb-2">TIER 3</div>
            <h2 className="text-2xl font-bold mb-2">X10 Signal</h2>
            <div className="text-4xl font-bold mb-6">$249<span className="text-lg text-gray-400">/mo</span></div>
            <ul className="space-y-3 text-gray-300 mb-8 text-sm">
              <li>Everything in Signal Synthesizer</li>
              <li>20 top trading accounts on X</li>
              <li>Perps, derivatives, synthetics</li>
              <li>Equities, commodities, FX</li>
              <li>Every 30 min during market hours</li>
              <li>Confluence scoring on keyword matches</li>
            </ul>
            <a
              href="https://buy.stripe.com/test_prod_UTmCN8WfEm86rk"
              className="block w-full text-center bg-white text-black font-semibold py-3 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Subscribe
            </a>
          </div>

          {/* Card 5 — X20 Signal */}
          <div className="border border-gray-800 rounded-2xl p-8 hover:border-[#00c853] transition-colors">
            <div className="text-[#00c853] text-sm font-semibold mb-2">TIER 4</div>
            <h2 className="text-2xl font-bold mb-2">X20 Signal</h2>
            <div className="text-4xl font-bold mb-6">$449<span className="text-lg text-gray-400">/mo</span></div>
            <ul className="space-y-3 text-gray-300 mb-8 text-sm">
              <li>Everything in X10 Signal</li>
              <li>Full X search beyond 20 accounts</li>
              <li>Cross-asset correlation scoring</li>
              <li>Instant high-confluence alerts (4+)</li>
              <li>End-of-day synthesis report</li>
              <li>15-minute cadence</li>
              <li>Includes Short Squeeze Radar</li>
            </ul>
            <a
              href="https://buy.stripe.com/test_prod_UTmCJV925O2pvU"
              className="block w-full text-center bg-white text-black font-semibold py-3 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Subscribe
            </a>
          </div>

          {/* Card 6 — PredictionCore */}
          <div className="border border-gray-800 rounded-2xl p-8 hover:border-[#00c853] transition-colors">
            <div className="text-[#00c853] text-sm font-semibold mb-2">TIER 5</div>
            <h2 className="text-2xl font-bold mb-2">PredictionCore</h2>
            <div className="text-4xl font-bold mb-6">$299<span className="text-lg text-gray-400">/mo</span></div>
            <ul className="space-y-3 text-gray-300 mb-8 text-sm">
              <li>Everything in X10 Signal</li>
              <li>Polymarket, Kalshi, DraftKings</li>
              <li>X sentiment, 538, ESPN BPI</li>
              <li>Politics, sports, crypto, economics</li>
              <li>Consensus probability + divergence alerts</li>
              <li>4x daily reports</li>
            </ul>
            <a
              href="https://buy.stripe.com/test_prod_UTmghR9ygJVPZb"
              className="block w-full text-center bg-white text-black font-semibold py-3 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Subscribe
            </a>
          </div>

          {/* Card 7 — Prediction Pro */}
          <div className="border border-gray-800 rounded-2xl p-8 hover:border-[#00c853] transition-colors">
            <div className="text-[#00c853] text-sm font-semibold mb-2">TIER 6</div>
            <h2 className="text-2xl font-bold mb-2">Prediction Pro</h2>
            <div className="text-4xl font-bold mb-6">$499<span className="text-lg text-gray-400">/mo</span></div>
            <ul className="space-y-3 text-gray-300 mb-8 text-sm">
              <li>Everything in all tiers</li>
              <li>Instant shift alerts (&gt;5% moves)</li>
              <li>New high-volume market detection</li>
              <li>X sentiment divergence tracking</li>
              <li>End-of-day probability shift report</li>
              <li>Custom watchlists (coming soon)</li>
              <li>Includes Short Squeeze Radar</li>
            </ul>
            <a
              href="https://buy.stripe.com/test_prod_UTmhMhmW6G3r4D"
              className="block w-full text-center bg-white text-black font-semibold py-3 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Subscribe
            </a>
          </div>

          {/* Card 8 — The Sunday Setup */}
          <div className="border border-[#00c853] rounded-2xl p-8 relative overflow-hidden">
            <div className="absolute top-0 right-0 bg-[#00c853] text-black text-xs font-bold px-3 py-1 rounded-bl-lg">
              INCLUDED FREE
            </div>
            <div className="text-[#00c853] text-sm font-semibold mb-2">BONUS</div>
            <h2 className="text-2xl font-bold mb-2">The Sunday Setup</h2>
            <div className="text-4xl font-bold mb-6">$0<span className="text-lg text-gray-400">/mo</span></div>
            <ul className="space-y-3 text-gray-300 mb-8 text-sm">
              <li>Every Sunday at 6:00 PM EST</li>
              <li>Full week-ahead economic calendar</li>
              <li>Top 15 earnings with consensus</li>
              <li>Geopolitical risk watchlist</li>
              <li>Options expiration + max pain</li>
              <li>XSignal synthesis for the week</li>
              <li>Posted FREE on X/Twitter</li>
              <li><b>Included with every tier</b></li>
            </ul>
            <a
              href="https://buy.stripe.com/test_prod_UTnDozUig2aYiV"
              className="block w-full text-center bg-[#00c853] text-black font-semibold py-3 rounded-lg hover:bg-[#00a844] transition-colors"
            >
              Subscribe to Any Tier
            </a>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-20 text-center text-gray-500 text-sm">
          <p>Fully automated by KimiClaw AI. Cancel anytime in Stripe.</p>
          <p className="mt-2">Not financial advice. Informational purposes only.</p>
        </div>
      </div>
    </main>
  );
}
