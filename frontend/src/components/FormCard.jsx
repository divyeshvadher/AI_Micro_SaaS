import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/card';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Link2, Loader2, Sparkles } from 'lucide-react';
import { mockCreateLink } from '../mock';

const FormCard = ({ onLinkCreated }) => {
  const [url, setUrl] = useState('');
  const [expiryText, setExpiryText] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const validateUrl = (urlString) => {
    try {
      const urlObj = new URL(urlString);
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
      return false;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Reset errors
    const newErrors = {};
    
    // Validate URL
    if (!url.trim()) {
      newErrors.url = 'Please enter a URL';
    } else if (!validateUrl(url)) {
      newErrors.url = 'Please enter a valid URL (must start with http:// or https://)';
    }
    
    // Validate expiry text
    if (!expiryText.trim()) {
      newErrors.expiryText = 'Please describe when the link should expire';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    // Clear errors and submit
    setErrors({});
    setLoading(true);
    
    try {
      const result = await mockCreateLink(url, expiryText);
      onLinkCreated(result);
    } catch (error) {
      setErrors({ submit: 'Something went wrong. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-lg border-cyan-100 hover:shadow-xl transition-all duration-300">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl flex items-center gap-2">
          <Link2 className="w-6 h-6 text-cyan-600" />
          Create Smart Link
        </CardTitle>
        <CardDescription>
          Enter your URL and describe how you want it to expire
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="url" className="text-sm font-medium">
              Original URL
            </Label>
            <Input
              id="url"
              type="text"
              placeholder="https://example.com/your-long-url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className={`transition-all duration-200 ${errors.url ? 'border-red-500 focus-visible:ring-red-500' : 'focus-visible:ring-cyan-500'}`}
            />
            {errors.url && (
              <p className="text-sm text-red-500 animate-in slide-in-from-top-1">{errors.url}</p>
            )}
            {!errors.url && url && validateUrl(url) && (
              <p className="text-sm text-green-600 animate-in slide-in-from-top-1">✓ Valid URL</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="expiry" className="text-sm font-medium">
              Expiry Instructions
            </Label>
            <Textarea
              id="expiry"
              placeholder="e.g., 'expire after 3 clicks or by tomorrow night' or 'expire in 24 hours'"
              value={expiryText}
              onChange={(e) => setExpiryText(e.target.value)}
              rows={3}
              className={`transition-all duration-200 resize-none ${errors.expiryText ? 'border-red-500 focus-visible:ring-red-500' : 'focus-visible:ring-cyan-500'}`}
            />
            {errors.expiryText && (
              <p className="text-sm text-red-500 animate-in slide-in-from-top-1">{errors.expiryText}</p>
            )}
            <p className="text-xs text-gray-500">
              Describe in natural language when you want this link to stop working
            </p>
          </div>

          {errors.submit && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{errors.submit}</p>
            </div>
          )}

          <Button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-cyan-600 to-cyan-700 hover:from-cyan-700 hover:to-cyan-800 text-white font-medium py-6 transition-all duration-200 hover:shadow-lg disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Creating Smart Link...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Create Smart Link
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default FormCard;
