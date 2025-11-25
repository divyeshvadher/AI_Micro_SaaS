import React, { useState } from 'react';
import FormCard from '../components/FormCard';
import ResultCard from '../components/ResultCard';
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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-cyan-50 to-blue-50">
      {/* Header */}
      <header className="pt-16 pb-12 px-4">
        <div className="max-w-4xl mx-auto text-center space-y-4">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-cyan-600 to-blue-600 rounded-xl shadow-lg">
              <Ghost className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-900 via-cyan-900 to-blue-900 bg-clip-text text-transparent">
              GhostLink
            </h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Create self-destructing smart links from any URL
          </p>
          <p className="text-base text-gray-500 max-w-xl mx-auto">
            Set custom expiry rules in plain English — links that vanish after N clicks, hours, or days
          </p>
          
          {/* Feature Pills */}
          <div className="flex flex-wrap items-center justify-center gap-3 pt-4">
            <div className="flex items-center gap-2 px-4 py-2 bg-white border border-cyan-200 rounded-full shadow-sm">
              <Zap className="w-4 h-4 text-cyan-600" />
              <span className="text-sm text-gray-700">Natural Language Rules</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-white border border-cyan-200 rounded-full shadow-sm">
              <Ghost className="w-4 h-4 text-cyan-600" />
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
                  className="text-cyan-700 hover:text-cyan-800 font-medium text-sm underline underline-offset-4 transition-colors duration-200"
                >
                  Create Another Link
                </button>
              </div>
            </section>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-gray-200 bg-white/50 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-sm text-gray-500">
            Built with React • Currently using mocked data • Ready for backend integration
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
