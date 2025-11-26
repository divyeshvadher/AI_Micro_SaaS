import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/card';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Link2, Loader2, Sparkles } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
      const response = await axios.post(`${API}/links/create`, {
        originalUrl: url,
        expiryText: expiryText
      });
      
      if (response.data.success) {
        onLinkCreated(response.data.data);
      } else {
        setErrors({ submit: 'Failed to create link. Please try again.' });
      }
    } catch (error) {
      console.error('Error creating link:', error);
      setErrors({ submit: error.response?.data?.detail || 'Something went wrong. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-xl hover:shadow-2xl transition-all duration-300 rounded-2xl bg-white/80 backdrop-blur border border-slate-200 relative">
      <div className="absolute inset-0 rounded-2xl pointer-events-none" style={{boxShadow:'0 0 0 1px rgba(99,102,241,0.15)'}}></div>
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl flex items-center gap-2">
          <Link2 className="w-6 h-6 text-teal-600" />
          Create {APP_NAME}
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
              className={`transition-all duration-200 rounded-xl ${errors.url ? 'border-red-500 focus-visible:ring-red-500' : 'focus-visible:ring-teal-500'} bg-white/70 backdrop-blur`}
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
              className={`transition-all duration-200 resize-none rounded-xl ${errors.expiryText ? 'border-red-500 focus-visible:ring-red-500' : 'focus-visible:ring-teal-500'} bg-white/70 backdrop-blur`}
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
            className="w-full bg-gradient-to-r from-teal-600 via-cyan-600 to-purple-600 hover:brightness-105 text-white font-medium py-6 transition-all duration-300 hover:shadow-xl rounded-xl disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Creating {APP_NAME}...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Create {APP_NAME}
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default FormCard;
import { APP_NAME } from '../config/app';
