import React, { useState, useEffect } from 'react';

// Define plugin message types for better type safety
interface PluginMessage {
  type: string;
  [key: string]: any;
}

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    // Listen for messages from the plugin
    const handleMessage = (event: MessageEvent) => {
      if (event.data.pluginMessage) {
        const msg = event.data.pluginMessage;
        console.log("Message from plugin:", msg);
        
        if (msg.type === 'LOGIN_RESPONSE') {
          setIsLoading(false);
          if (msg.success) {
            console.log('Login successful!');
          } else {
            setErrorMessage(msg.message || 'Authentication failed');
          }
        }
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage('');
    
    // Send message to plugin
    parent.postMessage({
      pluginMessage: {
        type: 'login',
        email,
        password
      }
    }, '*');
  };

  const togglePasswordVisibility = () => {
    setIsPasswordVisible(!isPasswordVisible);
  };

  return (
    <div className="flex flex-col w-full h-full bg-white">
      <div className="p-6 flex-1">
        <div className="w-full max-w-[350px] mx-auto space-y-6">
          <div className="space-y-2">
            <h1 className="text-3xl font-semibold text-[#0F172A] tracking-tight">Login</h1>
            <p className="text-sm text-[#64748B]">Enter your email and password to login to your account</p>
          </div>

          {errorMessage && (
            <div className="bg-red-50 text-red-500 p-2 rounded-md text-sm border border-red-200">
              {errorMessage}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="email" className="block text-sm font-medium text-[#0F172A]">
                Email
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="johndoe@mail.com"
                className="w-full h-10 px-3 py-2 border border-[#CBD5E1] rounded-md text-sm shadow-[0px_1px_2px_rgba(0,0,0,0.05)] focus:outline-none focus:ring-1 focus:ring-[#0F172A] focus:border-[#0F172A]"
                required
              />
            </div>

            <div className="space-y-1">
              <div className="space-y-2">
                <label htmlFor="password" className="block text-sm font-medium text-[#0F172A]">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={isPasswordVisible ? 'text' : 'password'}
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="******"
                    className="w-full h-10 px-3 py-2 border border-[#CBD5E1] rounded-md text-sm shadow-[0px_1px_2px_rgba(0,0,0,0.05)] focus:outline-none focus:ring-1 focus:ring-[#0F172A] focus:border-[#0F172A]"
                    required
                  />
                  <button
                    type="button"
                    onClick={togglePasswordVisibility}
                    className="absolute right-3 top-2.5 text-[#64748B]"
                  >
                    {isPasswordVisible ? (
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"></path>
                        <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"></path>
                        <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"></path>
                        <line x1="2" x2="22" y1="2" y2="22"></line>
                      </svg>
                    ) : (
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                      </svg>
                    )}
                  </button>
                </div>
              </div>
              <div className="text-right">
                <a href="#" className="text-xs text-[#64748B] hover:text-[#334155]">
                  Forgot your password?
                </a>
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <button
                type="submit"
                className="w-full h-9 bg-[#0F172A] text-white rounded-md text-sm font-medium shadow-sm hover:bg-[#1E293B] focus:outline-none focus:ring-2 focus:ring-[#0F172A] focus:ring-offset-2 disabled:opacity-70 transition-colors"
                disabled={isLoading}
              >
                {isLoading ? 'Logging in...' : 'Login'}
              </button>
              <button
                type="button"
                className="w-full h-9 bg-white text-[#0F172A] border border-[#CBD5E1] rounded-md text-sm font-medium shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#0F172A] focus:ring-offset-2 transition-colors"
              >
                Login with Google
              </button>
            </div>
          </form>

          <div className="text-center text-sm font-medium text-[#0F172A]">
            Don't have an account ? <a href="#" className="underline">Sign up</a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;