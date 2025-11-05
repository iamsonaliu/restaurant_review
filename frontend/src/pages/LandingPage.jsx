import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';

export default function LandingPage() {
  const [stats, setStats] = useState({
    restaurants: 0,
    reviews: 0,
    cities: 4
  });

  useEffect(() => {
    // Animate numbers on load
    const animateValue = (key, end, duration) => {
      let start = 0;
      const increment = end / (duration / 16);
      const timer = setInterval(() => {
        start += increment;
        if (start >= end) {
          setStats(prev => ({ ...prev, [key]: end }));
          clearInterval(timer);
        } else {
          setStats(prev => ({ ...prev, [key]: Math.floor(start) }));
        }
      }, 16);
    };

    animateValue('restaurants', 450, 2000);
    animateValue('reviews', 1200, 2000);
  }, []);

  const features = [
    {
      icon: "🔍",
      title: "Smart Discovery",
      description: "Find restaurants with advanced filters for cuisine, price, and ratings"
    },
    {
      icon: "⭐",
      title: "Trusted Reviews",
      description: "Read authentic reviews from verified users across Uttarakhand"
    },
    {
      icon: "📊",
      title: "Data Analytics",
      description: "Explore trends and insights about restaurants in your city"
    },
    {
      icon: "💝",
      title: "Personalized",
      description: "Save favorites and get recommendations based on your preferences"
    }
  ];

  const cities = [
    { name: "Dehradun", count: "150+", image: "🏔️" },
    { name: "Haridwar", count: "120+", image: "🕉️" },
    { name: "Mussoorie", count: "90+", image: "🌄" },
    { name: "Rishikesh", count: "90+", image: "🧘" }
  ];

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero-section relative overflow-hidden py-20 px-4">
        <div className="container-custom">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="hero-content animate-fade-in">
              <h1 className="text-5xl lg:text-6xl font-bold mb-6 leading-tight">
                Discover the Best
                <span className="text-gradient block mt-2">
                  Restaurants in Uttarakhand
                </span>
              </h1>
              <p className="text-xl mb-8 opacity-80">
                Your guide to authentic dining experiences across Dehradun, Haridwar, Mussoorie, and Rishikesh
              </p>
              <div className="flex flex-wrap gap-4">
                <Link to="/discover" className="btn btn-primary text-lg">
                  <span>Explore Now</span>
                  <span>→</span>
                </Link>
                <Link to="/register" className="btn btn-outline text-lg">
                  Join DineWise
                </Link>
              </div>
            </div>
            
            <div className="hero-image animate-slide-in">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-orange-400 to-pink-600 rounded-3xl opacity-20 blur-3xl"></div>
                <div className="relative grid grid-cols-2 gap-4">
                  <div className="card p-6 text-center transform hover:scale-105 transition-transform">
                    <div className="text-4xl mb-2">🍛</div>
                    <div className="text-2xl font-bold text-gradient">{stats.restaurants}+</div>
                    <div className="text-sm opacity-70">Restaurants</div>
                  </div>
                  <div className="card p-6 text-center transform hover:scale-105 transition-transform">
                    <div className="text-4xl mb-2">⭐</div>
                    <div className="text-2xl font-bold text-gradient">{stats.reviews}+</div>
                    <div className="text-sm opacity-70">Reviews</div>
                  </div>
                  <div className="card p-6 text-center transform hover:scale-105 transition-transform">
                    <div className="text-4xl mb-2">🏙️</div>
                    <div className="text-2xl font-bold text-gradient">{stats.cities}</div>
                    <div className="text-sm opacity-70">Cities</div>
                  </div>
                  <div className="card p-6 text-center transform hover:scale-105 transition-transform">
                    <div className="text-4xl mb-2">👥</div>
                    <div className="text-2xl font-bold text-gradient">500+</div>
                    <div className="text-sm opacity-70">Active Users</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section py-20 px-4" style={{ backgroundColor: 'var(--bg-secondary)' }}>
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Why Choose DineWise?</h2>
            <p className="text-xl opacity-70">Everything you need to find your next favorite restaurant</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="card text-center hover:border-orange-500 transition-all duration-300"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="text-5xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="opacity-70">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Cities Section */}
      <section className="cities-section py-20 px-4">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Explore by City</h2>
            <p className="text-xl opacity-70">Discover authentic flavors across Uttarakhand</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {cities.map((city, index) => (
              <Link
                key={index}
                to={`/discover?city=${city.name}`}
                className="card group cursor-pointer hover:shadow-2xl transition-all duration-300"
              >
                <div className="text-center">
                  <div className="text-6xl mb-4 transform group-hover:scale-110 transition-transform">
                    {city.image}
                  </div>
                  <h3 className="text-2xl font-bold mb-2">{city.name}</h3>
                  <p className="text-lg text-gradient font-semibold">{city.count} restaurants</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section py-20 px-4" style={{ backgroundColor: 'var(--accent-light)' }}>
        <div className="container-custom text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Start Exploring?</h2>
          <p className="text-xl mb-8 opacity-80 max-w-2xl mx-auto">
            Join thousands of food lovers discovering the best restaurants in Uttarakhand
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link to="/discover" className="btn btn-primary text-lg">
              Browse Restaurants
            </Link>
            <Link to="/register" className="btn btn-secondary text-lg">
              Create Account
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}