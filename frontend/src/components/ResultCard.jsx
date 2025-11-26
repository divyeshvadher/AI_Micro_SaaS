import React, { useEffect, useState, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Copy, Check, ExternalLink, Clock, MousePointerClick } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ResultCard = ({ linkData }) => {
  const [copied, setCopied] = useState(false);
  const [current, setCurrent] = useState(linkData);
  const { toast } = useToast();

  const handleCopy = () => {
    navigator.clipboard.writeText(current.shortLink);
    setCopied(true);
    toast({
      title: 'Copied!',
      description: 'Short link copied to clipboard',
    });
    setTimeout(() => setCopied(false), 2000);
  };

  const getProgressPercentage = () => {
    if (current.expiryInfo.type === 'clicks' && current.expiryInfo.clickLimit) {
      return (current.expiryInfo.currentClicks / current.expiryInfo.clickLimit) * 100;
    }
    return 0;
  };

  const computeEffectiveStatus = () => {
    const info = current.expiryInfo || {};
    const hasClickLimit = typeof info.clickLimit === 'number' && info.clickLimit !== null;
    const clicks = info.currentClicks || 0;
    const byClicksExpired = hasClickLimit && clicks >= info.clickLimit;
    let byTimeExpired = false;
    if (info.timeLimit) {
      try {
        const tl = new Date(info.timeLimit);
        byTimeExpired = Date.now() >= tl.getTime();
      } catch {}
    }
    return (byClicksExpired || byTimeExpired) ? 'expired' : (current.status || 'active');
  };

  useEffect(() => {
    setCurrent(linkData);
  }, [linkData]);

  const fetchStatus = useCallback(async () => {
    if (!current?.shortCode) return;
    try {
      const res = await fetch(`${API}/links/${current.shortCode}`);
      const json = await res.json();
      if (json.success) {
        setCurrent(prev => ({
          ...prev,
          originalUrl: json.data.originalUrl,
          status: json.data.status,
          expiryInfo: {
            ...prev.expiryInfo,
            ...json.data.expiryInfo,
          }
        }));
      }
    } catch {}
  }, [current?.shortCode]);

  useEffect(() => {
    let timer;
    if (current?.shortCode) {
      fetchStatus();
      timer = setInterval(fetchStatus, 3000);
    }
    return () => timer && clearInterval(timer);
  }, [current?.shortCode, fetchStatus]);

  useEffect(() => {
    const onVisibility = () => {
      if (document.visibilityState === 'visible') fetchStatus();
    };
    document.addEventListener('visibilitychange', onVisibility);
    return () => document.removeEventListener('visibilitychange', onVisibility);
  }, [fetchStatus]);

  const handleLinkClick = () => {
    setTimeout(fetchStatus, 800);
    setTimeout(fetchStatus, 2000);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-xl animate-in slide-in-from-bottom-4 duration-500 rounded-2xl bg-white/80 backdrop-blur border border-slate-200">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl">Your {APP_NAME} is Ready</CardTitle>
          <Badge 
            variant="secondary" 
            className={`${
              computeEffectiveStatus() === 'active' 
                ? 'bg-teal-100 text-teal-800 border-teal-200' 
                : 'bg-red-100 text-red-800 border-red-200'
            }`}
          >
            {computeEffectiveStatus() === 'active' ? '● Active' : '● Expired'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Short Link Display */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Short Link</label>
          <div className="flex gap-2">
            <a
              href={current.shortLink}
              target="_blank"
              rel="noopener noreferrer"
              onClick={handleLinkClick}
              className="flex-1 p-3 bg-white/70 backdrop-blur border border-gray-200 rounded-xl font-mono text-sm break-all text-teal-700 hover:text-teal-800 underline underline-offset-2"
            >
              {current.shortLink}
            </a>
            <Button
              onClick={handleCopy}
              variant="outline"
              className="px-4 rounded-xl hover:bg-teal-50 hover:border-teal-300 transition-all duration-200"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-600" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Original URL */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Original URL</label>
            <div className="flex items-center gap-2 p-3 bg-white/70 backdrop-blur border border-gray-200 rounded-xl">
              <ExternalLink className="w-4 h-4 text-gray-500 flex-shrink-0" />
            <span className="text-sm text-gray-600 break-all">{current.originalUrl}</span>
            </div>
          </div>

        {/* Expiry Info */}
          <div className="space-y-3 p-4 bg-white/70 backdrop-blur border border-teal-200 rounded-2xl">
            <div className="flex items-start gap-2">
              <Clock className="w-5 h-5 text-teal-600 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">Expiry Rule</p>
                <p className="text-sm text-gray-700 mt-1">{current.expiryInfo.summary}</p>
              </div>
            </div>

          {/* Click Progress */}
          {(current.expiryInfo.type === 'clicks' || current.expiryInfo.type === 'hybrid') && current.expiryInfo.clickLimit && (
            <div className="space-y-2 mt-4">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-1">
                  <MousePointerClick className="w-4 h-4 text-teal-600" />
                  <span className="font-medium">Clicks Used</span>
                </div>
                <span className="text-gray-600">
                  {Math.min(current.expiryInfo.currentClicks, current.expiryInfo.clickLimit)} / {current.expiryInfo.clickLimit}
                </span>
              </div>
              <Progress 
                value={getProgressPercentage()} 
                className="h-2"
              />
            </div>
          )}
        </div>

        {/* Info Message */}
          <div className="p-3 bg-teal-50 border border-teal-200 rounded-xl">
            <p className="text-xs text-green-800">
              <strong>Success!</strong> Your {APP_NAME} is now active and will automatically expire based on your rules.
            </p>
          </div>
      </CardContent>
    </Card>
  );
};

export default ResultCard;
import { APP_NAME } from '../config/app';
