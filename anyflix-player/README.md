# Anyflix Clone

A modern Anyflix clone built with React, TypeScript, and TailwindCSS. Features a beautiful dark theme, smooth animations, and real movie data from TMDB API.

## Features

- 🎬 Browse trending, popular, and top-rated movies
- 🔥 Anyflix-style hero banner with movie details
- 📱 Responsive design for desktop and mobile
- ⚡ Smooth horizontal scrolling carousels
- 🎨 Dark theme with Anyflix-inspired design
- 🔍 Movie search functionality (coming soon)
- 👤 Authentication pages
- 🎯 Hover effects and smooth animations

## Tech Stack

- **Frontend**: React 18, TypeScript, TailwindCSS
- **API**: TMDB (The Movie Database)
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **State Management**: React Hooks
- **Icons**: Lucide React
- **Build Tool**: Vite

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- TMDB API key (optional - demo key included)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Anyflix-clone
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:8080](http://localhost:8080) in your browser

### TMDB API Setup (Optional)

The app includes a demo API key for TMDB. For production use:

1. Create a free account at [TMDB](https://www.themoviedb.org/)
2. Get your API key from the API settings
3. Replace the API key in `src/services/tmdb.ts`

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Hero.tsx        # Main hero banner
│   ├── MovieCard.tsx   # Individual movie card
│   ├── MovieRow.tsx    # Horizontal movie carousel
│   └── Navbar.tsx      # Navigation header
├── pages/              # Page components
│   ├── Home.tsx        # Main landing page
│   └── Auth.tsx        # Authentication page
├── services/           # API services
│   └── tmdb.ts         # TMDB API integration
├── types/              # TypeScript type definitions
│   └── movie.ts        # Movie-related types
└── styles/             # Global styles and design system
    └── index.css       # Anyflix-inspired design tokens
```

## Design System

The app uses a carefully crafted design system inspired by Anyflix:

- **Colors**: Deep blacks, Anyflix red (#E50914), subtle grays
- **Typography**: Clean, modern fonts with excellent contrast
- **Animations**: Smooth transitions and hover effects
- **Layout**: Responsive grid system with mobile-first approach

## API Integration

The app fetches real movie data from TMDB API:

- Trending movies
- Popular movies  
- Top rated movies
- Movies by genre (Action, Comedy, etc.)
- Movie details and images

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is for educational purposes. Anyflix is a trademark of Anyflix, Inc.