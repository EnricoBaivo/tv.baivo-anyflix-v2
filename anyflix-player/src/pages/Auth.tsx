import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const Auth = () => {
  const [isSignIn, setIsSignIn] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement authentication logic
    console.log('Form submitted:', formData);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      {/* Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-50"
        style={{
          backgroundImage: `url('https://assets.nflxext.com/ffe/siteui/vlv3/9d3533b2-0e2b-40b2-95e0-ecd7979cc88b/a3873901-5b7c-46eb-b9fa-12fea5197bd3/US-en-20240311-popsignuptwoweeks-perspective_alpha_website_small.jpg')`,
        }}
      />
      
      {/* Content */}
      <div className="relative z-10 w-full max-w-md mx-auto p-6">
        <div className="bg-black/75 backdrop-blur-sm rounded-lg p-8">
          {/* Logo */}
          <Link to="/" className="block text-center mb-8">
            <span className="text-primary text-3xl font-bold">Anyflix</span>
          </Link>

          {/* Form Title */}
          <h1 className="text-white text-2xl font-bold mb-6">
            {isSignIn ? 'Sign In' : 'Sign Up'}
          </h1>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email" className="text-white">
                Email
              </Label>
              <Input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                className="bg-anyflix-dark-gray border-anyflix-gray text-white"
                placeholder="Enter your email"
              />
            </div>

            <div>
              <Label htmlFor="password" className="text-white">
                Password
              </Label>
              <Input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleInputChange}
                className="bg-anyflix-dark-gray border-anyflix-gray text-white"
                placeholder="Enter your password"
              />
            </div>

            {!isSignIn && (
              <div>
                <Label htmlFor="confirmPassword" className="text-white">
                  Confirm Password
                </Label>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  required
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="bg-anyflix-dark-gray border-anyflix-gray text-white"
                  placeholder="Confirm your password"
                />
              </div>
            )}

            <Button type="submit" className="w-full anyflix-button">
              {isSignIn ? 'Sign In' : 'Sign Up'}
            </Button>
          </form>

          {/* Toggle Sign In/Sign Up */}
          <div className="mt-6 text-center text-anyflix-light-gray">
            {isSignIn ? (
              <>
                New to ANYFLIX?{' '}
                <button
                  onClick={() => setIsSignIn(false)}
                  className="text-white hover:underline"
                >
                  Sign up now
                </button>
              </>
            ) : (
              <>
                Already have an account?{' '}
                <button
                  onClick={() => setIsSignIn(true)}
                  className="text-white hover:underline"
                >
                  Sign in
                </button>
              </>
            )}
          </div>

          {/* Additional Info */}
          <div className="mt-4 text-xs text-anyflix-light-gray">
            This page is protected by Google reCAPTCHA to ensure you're not a bot.
          </div>
        </div>
      </div>
    </div>
  );
};

export default Auth;