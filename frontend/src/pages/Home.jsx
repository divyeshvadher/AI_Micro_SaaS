import React, { useState } from 'react';
import FormCard from '../components/FormCard';
import ResultCard from '../components/ResultCard';
import { APP_NAME } from '../config/app';
import { Ghost, Zap } from 'lucide-react';

const Home = () => {
  const [createdLink, setCreatedLink] = useState(null);

  const handleLinkCreated = (linkData) => {
    setCreatedLink(linkData);
    // Smooth scroll to result
    setTimeout(() => {
      document.getElementById('result-section')?.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }, 100);
  };

  const handleCreateAnother = () => {
    setCreatedLink(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 via-slate-50 to-zinc-50">
      {/* Header */}
      <header className="pt-16 pb-12 px-4">
        <div className="max-w-4xl mx-auto text-center space-y-4">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 rounded-xl shadow-lg bg-gradient-to-br from-cyan-500/80 via-teal-500/80 to-purple-500/80"></div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-slate-900 via-teal-900 to-purple-900 bg-clip-text text-transparent">
              {APP_NAME}
            </h1>
          </div>
          <p className="text-xl text-gray-700 max-w-2xl mx-auto leading-relaxed">
            Create self-destructing smart links from any URL
          </p>
          <p className="text-base text-gray-600 max-w-xl mx-auto">
            Set custom expiry rules in plain English — links that vanish after clicks or time
          </p>
          
          {/* Feature Pills */}
          <div className="flex flex-wrap items-center justify-center gap-3 pt-4">
            <div className="flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur border border-cyan-200 rounded-full shadow-sm">
              <span className="inline-block w-4 h-4 rounded-full bg-gradient-to-r from-cyan-500 to-teal-500"></span>
              <span className="text-sm text-gray-700">Natural Language Rules</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur border border-teal-200 rounded-full shadow-sm">
              <span className="inline-block w-4 h-4 rounded-full bg-gradient-to-r from-purple-500 to-cyan-500"></span>
              <span className="text-sm text-gray-700">Auto-Expiring Links</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="px-4 pb-20">
        <div className="space-y-8">
          {/* Form Section */}
          <section>
            <FormCard onLinkCreated={handleLinkCreated} />
          </section>

          {/* Result Section */}
          {createdLink && (
            <section id="result-section" className="pt-4">
              <ResultCard linkData={createdLink} />
              
              {/* Create Another Button */}
              <div className="text-center mt-6">
                <button
                  onClick={handleCreateAnother}
                  className="text-teal-700 hover:text-teal-800 font-medium text-sm underline underline-offset-4 transition-colors duration-200"
                >
                  Create Another Link
                </button>
              </div>
            </section>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-gray-200 bg-white/70 backdrop-blur">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-sm text-gray-500">{APP_NAME} — AI-powered expiring links</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
