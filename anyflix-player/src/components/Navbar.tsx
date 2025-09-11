import React, { useState, useRef } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Search, Bell, User, Menu, X } from "lucide-react";
import SearchModal from "./search/SearchModal";
import { useWebOSNavigation } from "../hooks/useWebOSFocus";

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const navRef = useRef<HTMLDivElement>(null);

  const navLinks = [
    { name: "Home", path: "/" },
    { name: "TV Shows", path: "/tv-shows" },
    { name: "Movies", path: "/movies" },
    { name: "My List", path: "/my-list" },
  ];

  const isActive = (path: string) => location.pathname === path;

  // webOS TV navigation hook
  const { navigationMode, updateFocusableElements } = useWebOSNavigation({
    containerRef: navRef,
    onNavigate: (direction) => {
      if (direction === 'down' && !isMenuOpen) {
        setIsMenuOpen(true);
        return true; // Handled
      }
      return false; // Not handled, use default behavior
    },
    onBack: () => {
      if (isSearchOpen) {
        setIsSearchOpen(false);
        return true;
      } else if (isMenuOpen) {
        setIsMenuOpen(false);
        return true;
      } else {
        // Handle app-level back navigation
        if (window.history.length > 1) {
          navigate(-1);
          return true;
        } else {
          // Let default behavior handle exit confirmation
          return false;
        }
      }
    },
    autoFocus: true,
  });

  // Update focusable elements when menu state changes
  React.useEffect(() => {
    updateFocusableElements();
  }, [isMenuOpen, updateFocusableElements]);

  // Helper function to generate webOS-compatible button classes
  const getWebOSButtonClasses = (baseClasses: string, isActive?: boolean) => {
    const webOSClasses = [
      'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
      navigationMode === '5way' ? 'focus:ring-offset-4' : 'focus:ring-offset-1',
      'min-w-[75px] min-h-[50px] flex items-center justify-center',
      'transition-all duration-200',
    ].join(' ');

    const activeClasses = isActive ? 'bg-anyflix-gray/30' : '';
    
    return `${baseClasses} ${webOSClasses} ${activeClasses}`.trim();
  };

  return (
    <nav 
      ref={navRef}
      className="fixed top-0 w-full z-50 bg-anyflix-black/95 backdrop-blur-sm transition-all duration-300"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link 
              to="/" 
              className={getWebOSButtonClasses(
                "text-primary text-2xl font-bold focus:ring-offset-anyflix-black rounded-md px-2 py-1"
              )}
              tabIndex={0}
            >
              ANYFLIX
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8 ml-8">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                to={link.path}
                className={getWebOSButtonClasses(
                  `text-sm font-medium hover:text-anyflix-light-gray focus:ring-offset-anyflix-black rounded-md px-3 py-2 ${
                    isActive(link.path) ? "text-white" : "text-anyflix-light-gray"
                  }`,
                  isActive(link.path)
                )}
                tabIndex={0}
              >
                {link.name}
              </Link>
            ))}
          </div>

          {/* Right Side Icons */}
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsSearchOpen(true)}
              className={getWebOSButtonClasses(
                "text-white hover:text-anyflix-light-gray focus:ring-offset-anyflix-black rounded-md p-3"
              )}
              tabIndex={0}
              aria-label="Open search"
            >
              <Search className="h-5 w-5" />
            </button>
            <button 
              className={getWebOSButtonClasses(
                "text-white hover:text-anyflix-light-gray focus:ring-offset-anyflix-black rounded-md p-3"
              )}
              tabIndex={0}
              aria-label="Notifications"
            >
              <Bell className="h-5 w-5" />
            </button>
            <Link
              to="/auth"
              className={getWebOSButtonClasses(
                "text-white hover:text-anyflix-light-gray focus:ring-offset-anyflix-black rounded-md p-3"
              )}
              tabIndex={0}
              aria-label="User profile"
            >
              <User className="h-5 w-5" />
            </Link>

            {/* Mobile menu button */}
            <button
              className={getWebOSButtonClasses(
                "md:hidden text-white focus:ring-offset-anyflix-black rounded-md p-3"
              )}
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              tabIndex={0}
              aria-label={isMenuOpen ? "Close menu" : "Open menu"}
            >
              {isMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 bg-anyflix-dark-gray rounded-lg mt-2">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  to={link.path}
                  className={getWebOSButtonClasses(
                    `px-3 py-2 text-base font-medium rounded-md focus:ring-offset-anyflix-dark-gray ${
                      isActive(link.path)
                        ? "text-white bg-anyflix-gray"
                        : "text-anyflix-light-gray hover:text-white hover:bg-anyflix-gray"
                    }`,
                    isActive(link.path)
                  )}
                  onClick={() => setIsMenuOpen(false)}
                  tabIndex={0}
                >
                  {link.name}
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Search Modal */}
      <SearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
      />
    </nav>
  );
};

export default Navbar;
