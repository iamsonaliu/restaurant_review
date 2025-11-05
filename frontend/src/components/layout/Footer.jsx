import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="py-12 px-4 mt-20" style={{ backgroundColor: 'var(--bg-secondary)', borderTop: '1px solid var(--border)' }}>
      <div className="container-custom">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div>
            <Link to="/" className="flex items-center gap-2 text-2xl font-bold mb-4">
              <span className="text-3xl">🍽️</span>
              <span className="text-gradient">DineWise</span>
            </Link>
            <p className="opacity-70 mb-4">
              Your trusted guide to discovering authentic dining experiences across Uttarakhand.
            </p>
            <div className="flex gap-4">
              <a href="#" className="text-2xl hover:scale-110 transition-transform">📘</a>
              <a href="#" className="text-2xl hover:scale-110 transition-transform">📷</a>
              <a href="#" className="text-2xl hover:scale-110 transition-transform">🐦</a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-bold text-lg mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li><Link to="/discover" className="opacity-70 hover:opacity-100 hover:text-orange-500 transition-all">Discover</Link></li>
              <li><Link to="/analytics" className="opacity-70 hover:opacity-100 hover:text-orange-500 transition-all">Analytics</Link></li>
              <li><Link to="/about" className="opacity-70 hover:opacity-100 hover:text-orange-500 transition-all">About Us</Link></li>
              <li><Link to="/contact" className="opacity-70 hover:opacity-100 hover:text-orange-500 transition-all">Contact</Link></li>
            </ul>
          </div>

          {/* Cities */}
          <div>
            <h3 className="font-bold text-lg mb-4">Explore Cities</h3>
            <ul className="space-y-2">
              <li><Link to="/discover?city=Dehradun" className="opacity-70 hover:opacity-100 hover:text-orange-500 transition-all">Dehradun</Link></li>
              <li><Link to="/discover?city=Haridwar" className="opacity-70 hover:opacity-100 hover:text-orange-500 transition-all">Haridwar</Link></li>
              <li><Link to="/discover?city=Mussoorie" className="opacity-70 hover:opacity-100 hover:text-orange-500 transition-all">Mussoorie</Link></li>
              <li><Link to="/discover?city=Rishikesh" className="opacity-70 hover:opacity-100 hover:text-orange-500 transition-all">Rishikesh</Link></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-bold text-lg mb-4">Contact Us</h3>
            <ul className="space-y-2 opacity-70">
              <li>📧 support@dinewise.in</li>
              <li>📞 +91-XXXX-XXXXXX</li>
              <li>📍 Dehradun, Uttarakhand</li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t text-center opacity-70" style={{ borderColor: 'var(--border)' }}>
          <p>© 2024 DineWise. All rights reserved. | A DBMS Project by [Your Team Name]</p>
        </div>
      </div>
    </footer>
  );
}