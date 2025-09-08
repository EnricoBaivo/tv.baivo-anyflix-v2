import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        netflix: {
          red: "hsl(var(--netflix-red))",
          black: "hsl(var(--netflix-black))",
          "dark-gray": "hsl(var(--netflix-dark-gray))",
          gray: "hsl(var(--netflix-gray))",
          "light-gray": "hsl(var(--netflix-light-gray))",
          white: "hsl(var(--netflix-white))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: {
            height: "0",
          },
          to: {
            height: "var(--radix-accordion-content-height)",
          },
        },
        "accordion-up": {
          from: {
            height: "var(--radix-accordion-content-height)",
          },
          to: {
            height: "0",
          },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
      width: {
        "movie-xs": "180px", // Extra small screens
        "movie-sm": "240px", // Small screens - more usable size
        "movie-md": "300px", // Medium screens
        "movie-lg": "720px", // Large screens (as requested)
        "movie-xl": "960px", // Extra large screens - bigger
        "movie-2xl": "1200px", // 2XL screens - even bigger
        "movie-card": "280px", // Default movie card width
        "movie-poster": "320px", // Movie poster width
      },
      height: {
        "movie-xs": "270px", // Extra small screens (1.5:1 ratio)
        "movie-sm": "360px", // Small screens (1.5:1 ratio)
        "movie-md": "450px", // Medium screens (1.5:1 ratio)
        "movie-lg": "405px", // Large screens (16:9 ratio for 720px width)
        "movie-xl": "540px", // Extra large screens (16:9 ratio for 960px width)
        "movie-2xl": "675px", // 2XL screens (16:9 ratio for 1200px width)
        "movie-card": "420px", // Default movie card height (1.5:1 ratio)
        "movie-poster": "480px", // Movie poster height (1.5:1 ratio)
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config;
