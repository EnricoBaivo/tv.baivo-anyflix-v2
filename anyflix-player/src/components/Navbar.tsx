import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Search, User } from "lucide-react";
import { FocusZone } from "./navigation/FocusZone";
import { FocusableItem } from "./navigation/FocusableItem";
import { cn } from "../lib/utils";

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const navLinks = [
    { name: "Home", path: "/" },
    { name: "Aniworld", path: "/aniworld" },
    { name: "SerienStream", path: "/serienstream" },
  ];

  const isActive = (path: string) => location.pathname === path;

  const handleNavClick = (path: string) => {
    navigate(path);
  };

  const handleSearchClick = () => {
    // TODO: Open search modal when implemented
    console.log("Search clicked - modal not implemented yet");
  };

  return (
    <nav
      className="fixed top-0 w-full z-50 bg-anyflix-black"
      style={{
        // NO backdrop-blur - not supported in Chromium 79
        // Use solid background with opacity instead
        backgroundColor: "hsl(0 0% 8% / 0.95)",
        // Force hardware acceleration for stable rendering on webOS TV
        transform: "translateZ(0)",
        WebkitTransform: "translateZ(0)",
      }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <FocusZone
          id="navbar-zone"
          type="row"
          priority={-1}
          rememberFocus
          navigationAxis="horizontal"
          className="flex items-center justify-between h-20"
        >
          {/* Logo */}
          <div className="flex-shrink-0 mr-8">
            <FocusableItem
              id="nav-logo"
              onSelect={() => handleNavClick("/")}
              className={cn(
                "text-primary text-2xl font-bold rounded-md px-3 py-2",
                "cursor-pointer outline-none transition-all duration-300"
              )}
              focusClassName="ring-2 ring-primary ring-offset-2 ring-offset-background scale-105"
            >
              <Link to="/" className="pointer-events-none">
                ANYFLIX
              </Link>
            </FocusableItem>
          </div>

          {/* Navigation Links - Use mr-4 instead of gap for Chromium 79 compatibility */}
          <div className="flex items-center flex-1">
            {navLinks.map((link, index) => (
              <FocusableItem
                key={link.name}
                id={`nav-${link.name.toLowerCase()}`}
                onSelect={() => handleNavClick(link.path)}
                className={cn(
                  // Use mr-4 (margin-right) instead of gap for Chromium 79 compatibility
                  "px-4 py-2 rounded-md cursor-pointer outline-none transition-all duration-300",
                  index < navLinks.length - 1 && "mr-4",
                  isActive(link.path)
                    ? "text-white font-semibold"
                    : "text-anyflix-light-gray font-medium hover:text-white"
                )}
                focusClassName={cn(
                  "ring-2 ring-primary ring-offset-2 ring-offset-background scale-105",
                  isActive(link.path) && "bg-anyflix-red/20"
                )}
              >
                <Link to={link.path} className="pointer-events-none">
                  {link.name}
                </Link>
              </FocusableItem>
            ))}
          </div>

          {/* Right Side Icons - Use mr-4 instead of gap */}
          <div className="flex items-center">
            <FocusableItem
              id="nav-search"
              onSelect={handleSearchClick}
              className="text-white hover:text-anyflix-light-gray rounded-md p-3 cursor-pointer outline-none transition-all duration-300 mr-4"
              focusClassName="ring-2 ring-primary ring-offset-2 ring-offset-background scale-110"
            >
              <button
                aria-label="Open search"
                className="pointer-events-none flex items-center justify-center"
              >
                <Search className="h-5 w-5" />
              </button>
            </FocusableItem>

            <FocusableItem
              id="nav-user"
              onSelect={() => handleNavClick("/auth")}
              className="text-white hover:text-anyflix-light-gray rounded-md p-3 cursor-pointer outline-none transition-all duration-300"
              focusClassName="ring-2 ring-primary ring-offset-2 ring-offset-background scale-110"
            >
              <Link to="/auth" aria-label="User profile" className="pointer-events-none flex items-center justify-center">
                <User className="h-5 w-5" />
              </Link>
            </FocusableItem>
          </div>
        </FocusZone>
      </div>
    </nav>
  );
};

export default Navbar;
