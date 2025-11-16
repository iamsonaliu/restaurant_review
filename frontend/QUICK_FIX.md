# Quick Fix for Blank White Screen

## Immediate Steps

### 1. Check Browser Console
Press `F12` in your browser and check the Console tab for errors.

### 2. Verify Vite is Running
Make sure you see output like:
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 3. Try These Commands

```bash
cd frontend

# Clear cache and reinstall
rm -rf node_modules
rm package-lock.json
npm install

# Start dev server
npm run dev
```

### 4. Check These Common Issues

#### Missing Dependencies
```bash
npm install react react-dom react-router-dom
npm install -D tailwindcss postcss autoprefixer
```

#### Port Already in Use
If port 5173 is busy, Vite will use the next available port. Check the terminal output.

#### Browser Cache
- Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
- Or clear browser cache

### 5. Test Minimal App

If still blank, temporarily replace `src/App.jsx` with:

```jsx
function App() {
  return (
    <div style={{ padding: '20px', fontSize: '24px' }}>
      <h1>Frontend is Working!</h1>
      <p>If you see this, React is working correctly.</p>
    </div>
  );
}
export default App;
```

If this shows, the issue is in your components. If not, it's a build/setup issue.

### 6. Check Network Tab
In browser DevTools → Network tab:
- Look for `main.jsx` - should be status 200
- Look for any failed requests (red)

### 7. Verify File Structure
Make sure these files exist:
- `frontend/index.html`
- `frontend/src/main.jsx`
- `frontend/src/App.jsx`
- `frontend/src/index.css`

## Still Not Working?

Share the error message from browser console (F12 → Console tab)

