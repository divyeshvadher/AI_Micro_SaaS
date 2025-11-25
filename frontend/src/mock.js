// Mock data for GhostLink

export const generateMockShortLink = () => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let code = '';
  for (let i = 0; i < 6; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return `https://ghost.link/${code}`;
};

export const parseMockExpiry = (expiryText) => {
  // Simple mock parsing - returns a human-readable summary
  const text = expiryText.toLowerCase();
  
  if (text.includes('click')) {
    const clickMatch = text.match(/(\d+)\s*click/);
    const clicks = clickMatch ? clickMatch[1] : '3';
    return {
      summary: `Expires after ${clicks} clicks`,
      type: 'clicks',
      limit: parseInt(clicks),
      current: Math.floor(Math.random() * parseInt(clicks))
    };
  }
  
  if (text.includes('hour')) {
    const hourMatch = text.match(/(\d+)\s*hour/);
    const hours = hourMatch ? hourMatch[1] : '24';
    const expiryDate = new Date();
    expiryDate.setHours(expiryDate.getHours() + parseInt(hours));
    return {
      summary: `Expires in ${hours} hours (${expiryDate.toLocaleDateString()} at ${expiryDate.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})})`,
      type: 'time',
      expiryDate: expiryDate.toISOString()
    };
  }
  
  if (text.includes('day')) {
    const dayMatch = text.match(/(\d+)\s*day/);
    const days = dayMatch ? dayMatch[1] : '1';
    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + parseInt(days));
    return {
      summary: `Expires in ${days} day${days > 1 ? 's' : ''} (${expiryDate.toLocaleDateString()})`,
      type: 'time',
      expiryDate: expiryDate.toISOString()
    };
  }
  
  if (text.includes('tomorrow')) {
    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + 1);
    expiryDate.setHours(23, 59, 59);
    return {
      summary: `Expires tomorrow at 11:59 PM (${expiryDate.toLocaleDateString()})`,
      type: 'time',
      expiryDate: expiryDate.toISOString()
    };
  }
  
  // Default case
  const expiryDate = new Date();
  expiryDate.setDate(expiryDate.getDate() + 7);
  return {
    summary: `Expires in 7 days (${expiryDate.toLocaleDateString()})`,
    type: 'time',
    expiryDate: expiryDate.toISOString()
  };
};

export const mockCreateLink = async (url, expiryText) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  const shortLink = generateMockShortLink();
  const expiryInfo = parseMockExpiry(expiryText);
  
  return {
    shortLink,
    originalUrl: url,
    expiryInfo,
    status: 'active',
    createdAt: new Date().toISOString()
  };
};
