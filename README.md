# AccessRoadTracing

## Quick Start (Web Viewer)

1. **Install dependencies**  
   Open a terminal in the `Web` folder and run:
   ```
   npm install
   ```

2. **Add your LAS file**  
   Place your `.las` file (e.g., `GK_465_135.las`) in the `Web` folder.

3. **Start the development server**  
   ```
   npx vite
   ```
   The terminal will show a local URL (e.g., `http://localhost:5173`). Open it in your browser.

4. **Usage**  
   - The point cloud will be displayed.
   - Click two points in the viewer to generate and display a terrain profile between them.

---

**Requirements:**  
- Node.js and npm installed

**Notes:**  
- For large `.las` files, consider downsampling before loading in the browser.
- The viewer uses Three.js, loaders.gl, and Plotly.js.

