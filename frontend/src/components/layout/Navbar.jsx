import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

export default function Navbar({ theme, toggleTheme }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navbar fixed top-0 w-full z-50 shadow-md" style={{ backgroundColor: 'var(--bg-card)' }}>
      <div className="container-custom py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 text-2xl font-bold">
            <span className="text-4xl">🍽️</span>
            <span className="text-gradient">DineWise</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-8">
            <Link to="/discover" className="hover:text-orange-500 transition-colors font-medium">
              Discover
            </Link>
            <Link to="/analytics" className="hover:text-orange-500 transition-colors font-medium">
              Analytics
            </Link>
            
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="hover:text-orange-500 transition-colors font-medium">
                  Dashboard
                </Link>
                <div className="flex items-center gap-4">
                  <Link to="/profile" className="flex items-center gap-2 hover:text-orange-500 transition-colors">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-orange-400 to-pink-600 flex items-center justify-center text-white font-bold">
                      {user?.username?.charAt(0).toUpperCase()}
                    </div>
                    <span className="font-medium">{user?.username}</span>
                  </Link>
                  <button onClick={handleLogout} className="btn btn-outline py-2 px-4">
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <div className="flex gap-4">
                <Link to="/login" className="btn btn-outline py-2 px-4">
                  Login
                </Link>
                <Link to="/register" className="btn btn-primary py-2 px-4">
                  Sign Up
                </Link>
              </div>
            )}

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'light' ? '🌙' : '☀️'}
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 py-4 border-t" style={{ borderColor: 'var(--border)' }}>
            <div className="flex flex-col gap-4">
              <Link to="/discover" className="py-2 hover:text-orange-500 transition-colors" onClick={() => setIsMenuOpen(false)}>
                Discover
              </Link>
              <Link to="/analytics" className="py-2 hover:text-orange-500 transition-colors" onClick={() => setIsMenuOpen(false)}>
                Analytics
              </Link>
              
              {isAuthenticated ? (
                <>
                  <Link to="/dashboard" className="py-2 hover:text-orange-500 transition-colors" onClick={() => setIsMenuOpen(false)}>
                    Dashboard
                  </Link>
                  <Link to="/profile" className="py-2 hover:text-orange-500 transition-colors" onClick={() => setIsMenuOpen(false)}>
                    Profile
                  </Link>
                  <button onClick={() => { handleLogout(); setIsMenuOpen(false); }} className="btn btn-outline w-full">
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="btn btn-outline w-full" onClick={() => setIsMenuOpen(false)}>
                    Login
                  </Link>
                  <Link to="/register" className="btn btn-primary w-full" onClick={() => setIsMenuOpen(false)}>
                    Sign Up
                  </Link>
                </>
              )}
              
              <button onClick={toggleTheme} className="btn btn-outline w-full">
                {theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode'}
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
