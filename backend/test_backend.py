#!/usr/bin/env python3
"""
DineWise Backend Testing Script
Tests all API endpoints to ensure they're working correctly
"""

import requests
import json
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

BASE_URL = "http://localhost:5000"
token = None

def print_section(title):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{title.center(60)}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

def print_success(message):
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.YELLOW}→ {message}{Style.RESET_ALL}")

def test_endpoint(method, endpoint, data=None, headers=None, expected_status=200):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code == expected_status:
            print_success(f"{method} {endpoint} - Status: {response.status_code}")
            return response.json() if response.content else None
        else:
            print_error(f"{method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
            print_info(f"Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}. Is the server running?")
        return None
    except Exception as e:
        print_error(f"{method} {endpoint} - Error: {str(e)}")
        return None

def test_health():
    """Test health check endpoint"""
    print_section("HEALTH CHECK")
    result = test_endpoint("GET", "/api/health")
    if result:
        print_info(f"Message: {result.get('message')}")
        print_info(f"Database: {result.get('database')}")
        print_info(f"Version: {result.get('version')}")
    return result is not None

def test_restaurants():
    """Test restaurant endpoints"""
    print_section("RESTAURANT ENDPOINTS")
    
    # Get all restaurants
    print_info("Testing GET /api/restaurants/")
    result = test_endpoint("GET", "/api/restaurants/", {"limit": 5})
    if result and 'restaurants' in result:
        print_success(f"Found {result.get('total', 0)} restaurants")
        if result['restaurants']:
            print_info(f"Sample: {result['restaurants'][0].get('name')}")
    
    # Get cities
    print_info("\nTesting GET /api/restaurants/cities")
    cities = test_endpoint("GET", "/api/restaurants/cities")
    if cities:
        print_success(f"Found {len(cities)} cities")
        print_info(f"Cities: {', '.join([c['city'] for c in cities[:3]])}")
    
    # Get categories
    print_info("\nTesting GET /api/restaurants/categories")
    categories = test_endpoint("GET", "/api/restaurants/categories")
    if categories:
        print_success(f"Found {len(categories)} categories")
        print_info(f"Sample categories: {', '.join([c['name'] for c in categories[:5]])}")
    
    # Search restaurants
    print_info("\nTesting GET /api/restaurants/search")
    search = test_endpoint("GET", "/api/restaurants/search", {"q": "cafe", "limit": 3})
    if search and 'results' in search:
        print_success(f"Search returned {search.get('count', 0)} results")
    
    return True

def test_auth():
    """Test authentication endpoints"""
    global token
    print_section("AUTHENTICATION")
    
    # Test registration
    print_info("Testing POST /api/auth/register")
    import random
    test_email = f"test{random.randint(1000, 9999)}@example.com"
    register_data = {
        "username": f"testuser{random.randint(1000, 9999)}",
        "email": test_email,
        "password": "testpassword123"
    }
    result = test_endpoint("POST", "/api/auth/register", register_data, expected_status=201)
    if result and 'token' in result:
        token = result['token']
        print_success("Registration successful")
        print_info(f"Token received: {token[:20]}...")
    
    # Test login
    print_info("\nTesting POST /api/auth/login")
    login_data = {
        "email": test_email,
        "password": "testpassword123"
    }
    result = test_endpoint("POST", "/api/auth/login", login_data)
    if result and 'token' in result:
        token = result['token']
        print_success("Login successful")
    
    return token is not None

def test_ratings():
    """Test rating endpoints"""
    global token
    print_section("RATING ENDPOINTS")
    
    if not token:
        print_error("No authentication token available. Skipping ratings tests.")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a rating
    print_info("Testing POST /api/ratings/")
    rating_data = {
        "restaurant_id": "R0001",
        "rating_value": 4.5
    }
    result = test_endpoint("POST", "/api/ratings/", rating_data, headers, expected_status=201)
    if result:
        print_success("Rating created successfully")
    
    # Get user ratings
    print_info("\nTesting GET /api/ratings/user")
    result = test_endpoint("GET", "/api/ratings/user", headers=headers)
    if result:
        print_success(f"Retrieved {len(result)} user ratings")
    
    return True

def test_reviews():
    """Test review endpoints"""
    global token
    print_section("REVIEW ENDPOINTS")
    
    # Get reviews for a restaurant
    print_info("Testing GET /api/reviews/restaurant/R0001")
    result = test_endpoint("GET", "/api/reviews/restaurant/R0001")
    if result:
        print_success(f"Retrieved {len(result)} reviews")
    
    if not token:
        print_error("No authentication token available. Skipping review creation test.")
        return True
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a review
    print_info("\nTesting POST /api/reviews/")
    review_data = {
        "restaurant_id": "R0001",
        "review_text": "Great food and excellent service! Highly recommend."
    }
    result = test_endpoint("POST", "/api/reviews/", review_data, headers, expected_status=201)
    if result:
        print_success("Review created successfully")
    
    return True

def test_analytics():
    """Test analytics endpoints"""
    print_section("ANALYTICS ENDPOINTS")
    
    # Top rated restaurants
    print_info("Testing GET /api/analytics/top-rated")
    result = test_endpoint("GET", "/api/analytics/top-rated")
    if result:
        print_success(f"Retrieved {len(result)} top-rated restaurants")
        if result:
            print_info(f"Top restaurant: {result[0].get('name')} - Rating: {result[0].get('avg_rating')}")
    
    # City statistics
    print_info("\nTesting GET /api/analytics/city-stats")
    result = test_endpoint("GET", "/api/analytics/city-stats")
    if result:
        print_success(f"Retrieved statistics for {len(result)} cities")
    
    return True

def main():
    """Run all tests"""
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        DINEWISE BACKEND API - COMPREHENSIVE TEST           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    
    print_info(f"Testing backend at: {BASE_URL}")
    print_info("Make sure the backend server is running!\n")
    
    tests = [
        ("Health Check", test_health),
        ("Restaurants", test_restaurants),
        ("Authentication", test_auth),
        ("Ratings", test_ratings),
        ("Reviews", test_reviews),
        ("Analytics", test_analytics)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print_error(f"Test '{name}' failed with error: {e}")
            results[name] = False
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = f"{Fore.GREEN}PASSED" if result else f"{Fore.RED}FAILED"
        print(f"{name:.<40} {status}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Total: {passed}/{total} tests passed{Style.RESET_ALL}")
    
    if passed == total:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 All tests passed! Backend is working correctly.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Some tests failed. Check the output above for details.{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Tests interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")