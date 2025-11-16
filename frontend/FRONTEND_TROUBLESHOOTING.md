# Frontend Troubleshooting Guide

## Blank White Screen Issue

If you're seeing a blank white screen, follow these steps:

### Step 1: Check Browser Console
1. Open your browser's Developer Tools (F12)
2. Go to the "Console" tab
3. Look for any red error messages
4. Common errors:
   - `Cannot find module` - Missing import
   - `Uncaught TypeError` - JavaScript error
   - `Failed to compile` - Build error

### Step 2: Check Network Tab
1. In Developer Tools, go to "Network" tab
2. Refresh the page
3. Look for failed requests (red status codes)
4. Check if `main.jsx` is loading

### Step 3: Verify Dependencies
```bash
cd frontend
npm install
```

### Step 4: Clear Cache and Rebuild
```bash
cd frontend
rm -rf node_modules
rm package-lock.json
npm install
npm run dev
```

### Step 5: Check Vite Server
Make sure Vite is running on the correct port (usually 5173):
- Check terminal for: `Local: http://localhost:5173`
- Try accessing: http://localhost:5173

### Common Issues

#### Issue: "Cannot find module 'react'"
**Solution**: 
```bash
npm install react react-dom
```

#### Issue: "Failed to compile"
**Solution**: Check for syntax errors in your components

#### Issue: "Uncaught TypeError: Cannot read property"
**Solution**: Check if components are properly initialized

#### Issue: CSS not loading
**Solution**: 
```bash
npm install -D tailwindcss postcss autoprefixer
```

### Quick Fix: Test with Minimal App

If nothing works, try this minimal test:

1. Temporarily replace `App.jsx` content with:
```jsx
function App() {
  return <div>Hello World - Frontend is working!</div>;
}
export default App;
```

2. If this shows, the issue is in your components
3. If this doesn't show, the issue is in setup/build

