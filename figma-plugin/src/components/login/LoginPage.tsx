import React, { useState, useEffect } from "react";

declare global {
  interface Window {
    sendToPlugin: (msg: any) => void;
  }
}

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Communication avec le plugin Figma
  useEffect(() => {
    // Envoyer un signal que le composant est monté
    if (window.sendToPlugin) {
      window.sendToPlugin({ type: 'UI_READY' });
    }

    // Écouter les réponses du plugin
    const handleMessage = (event: MessageEvent) => {
      if (event.data.pluginMessage && event.data.pluginMessage.type === 'LOGIN_RESPONSE') {
        setIsLoading(false);
        if (event.data.pluginMessage.success) {
          // Login réussi - vous pourriez rediriger ici
          console.log("Login successful!");
        } else {
          // Login échoué
          setErrorMessage(event.data.pluginMessage.message || "Authentication failed");
        }
      }
    };

    // Ajouter l'écouteur d'événements
    window.addEventListener('message', handleMessage);

    // Nettoyer l'écouteur à la destruction du composant
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, []);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage("");

    if (window.sendToPlugin) {
      window.sendToPlugin({
        type: 'login',
        email,
        password
      });
    } else {
      console.error("sendToPlugin is not available");
      setIsLoading(false);
      setErrorMessage("Plugin communication error");
    }
  };

  const togglePassword = () => setPasswordVisible(!passwordVisible);

  return (
    <div className="flex flex-col w-[350px] p-6 space-y-6 bg-white rounded-lg">
      {/* Titre */}
      <h1 className="text-3xl font-semibold text-[#0F172A] -tracking-[0.75%]">
        Login
      </h1>

      {/* Sous-titre / Description */}
      <p className="text-sm text-[#64748B]">
        Enter your email and password to login to your account
      </p>

      {errorMessage && (
        <div className="text-red-500 text-sm font-medium bg-red-50 p-2 rounded border border-red-200">
          {errorMessage}
        </div>
      )}

      <form onSubmit={handleLogin} className="flex flex-col space-y-4">
        {/* Input Email */}
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium text-[#0F172A]">
            Email
          </label>
          <input
            type="email"
            placeholder="johndoe@mail.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="h-10 px-3 py-2 border border-[#CBD5E1] rounded-md shadow-[0px_1px_5px_0px_rgba(0,0,0,0.07)] text-sm outline-none focus:ring-2 focus:ring-blue-500"
            required
            disabled={isLoading}
          />
        </div>

        {/* Input Password */}
        <div className="flex flex-col space-y-1">
          <div className="flex flex-col space-y-2">
            <label className="text-sm font-medium text-[#0F172A]">
              Password
            </label>
            <div className="relative">
              <input
                type={passwordVisible ? "text" : "password"}
                placeholder="******"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full h-10 px-3 py-2 border border-[#CBD5E1] rounded-md shadow-[0px_1px_5px_0px_rgba(0,0,0,0.07)] text-sm outline-none focus:ring-2 focus:ring-blue-500 pr-10"
                required
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={togglePassword}
                className="absolute right-3 top-2.5 text-[#848484]"
                disabled={isLoading}
              >
                {passwordVisible ? (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"></path>
                    <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"></path>
                    <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"></path>
                    <line x1="2" x2="22" y1="2" y2="22"></line>
                  </svg>
                ) : (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                )}
              </button>
            </div>
          </div>
          <div className="flex justify-end">
            <a
              href="#"
              className="text-xs font-medium text-[#848484] hover:text-[#0F172A]"
            >
              Forgot your password?
            </a>
          </div>
        </div>

        {/* Boutons */}
        <div className="flex flex-col space-y-4 pt-2">
          {/* Login Button */}
          <button
            type="submit"
            className="w-full h-9 bg-[#0F172A] text-white font-medium text-sm rounded-md shadow-[0px_1px_5px_0px_rgba(0,0,0,0.07)] hover:bg-[#1e293b] transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
            disabled={isLoading}
          >
            {isLoading ? "Logging in..." : "Login"}
          </button>

          {/* Google Login Button */}
          <button
            type="button"
            className="w-full h-9 bg-white text-[#0F172A] font-medium text-sm border border-[#CBD5E1] rounded-md shadow-[0px_1px_5px_0px_rgba(0,0,0,0.07)] hover:bg-gray-50 transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
            disabled={isLoading}
            onClick={() => console.log("Google login")}
          >
            Login with Google
          </button>
        </div>
      </form>

      {/* Sign Up Text */}
      <div className="flex items-center justify-center space-x-1 text-sm font-medium">
        <span className="text-[#0F172A]">Don't have an account ?</span>
        <a href="#" className="text-[#0F172A] underline">
          Sign up
        </a>
      </div>
    </div>
  );
} 