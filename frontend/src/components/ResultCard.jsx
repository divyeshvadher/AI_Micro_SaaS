import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Copy, Check, ExternalLink, Clock, MousePointerClick } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const ResultCard = ({ linkData }) => {
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const handleCopy = () => {
    navigator.clipboard.writeText(linkData.shortLink);
    setCopied(true);
    toast({
      title: 'Copied!',
      description: 'Short link copied to clipboard',
    });
    setTimeout(() => setCopied(false), 2000);
  };

  const getProgressPercentage = () => {
    if (linkData.expiryInfo.type === 'clicks' && linkData.expiryInfo.clickLimit) {
      return (linkData.expiryInfo.currentClicks / linkData.expiryInfo.clickLimit) * 100;
    }
    return 0;
  };

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-lg border-cyan-100 animate-in slide-in-from-bottom-4 duration-500">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl">Your Smart Link is Ready!</CardTitle>
          <Badge 
            variant="secondary" 
            className={`${
              linkData.status === 'active' 
                ? 'bg-green-100 text-green-800 border-green-200' 
                : 'bg-red-100 text-red-800 border-red-200'
            }`}
          >
            {linkData.status === 'active' ? '● Active' : '● Expired'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Short Link Display */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Short Link</label>
          <div className="flex gap-2">
            <div className="flex-1 p-3 bg-gray-50 border border-gray-200 rounded-md font-mono text-sm break-all">
              {linkData.shortLink}
            </div>
            <Button
              onClick={handleCopy}
              variant="outline"
              className="px-4 hover:bg-cyan-50 hover:border-cyan-300 transition-all duration-200"
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
          <div className="flex items-center gap-2 p-3 bg-gray-50 border border-gray-200 rounded-md">
            <ExternalLink className="w-4 h-4 text-gray-500 flex-shrink-0" />
            <span className="text-sm text-gray-600 break-all">{linkData.originalUrl}</span>
          </div>
        </div>

        {/* Expiry Info */}
        <div className="space-y-3 p-4 bg-cyan-50 border border-cyan-200 rounded-lg">
          <div className="flex items-start gap-2">
            <Clock className="w-5 h-5 text-cyan-600 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-900">Expiry Rule</p>
              <p className="text-sm text-gray-700 mt-1">{linkData.expiryInfo.summary}</p>
            </div>
          </div>

          {/* Click Progress */}
          {(linkData.expiryInfo.type === 'clicks' || linkData.expiryInfo.type === 'hybrid') && linkData.expiryInfo.clickLimit && (
            <div className="space-y-2 mt-4">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-1">
                  <MousePointerClick className="w-4 h-4 text-cyan-600" />
                  <span className="font-medium">Clicks Used</span>
                </div>
                <span className="text-gray-600">
                  {linkData.expiryInfo.currentClicks} / {linkData.expiryInfo.clickLimit}
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
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-xs text-blue-800">
            <strong>Note:</strong> This is a mock preview. In the full version, this link will automatically expire based on your rules and track real clicks.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default ResultCard;
