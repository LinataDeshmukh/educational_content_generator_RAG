# Portfolio Website for RAG Educational Content Generator

This is a static portfolio website showcasing the RAG-Powered Educational Content Generator project. It's designed to be hosted on **GitHub Pages** to demonstrate your work.

**Project by:** Linata Deshmukh & Pranesh Kannan

## 🎯 Purpose

This portfolio website:
- Showcases your project in a professional manner
- Highlights technical skills and achievements
- Demonstrates understanding of RAG, AI/ML, and full-stack development
- Provides links to live demo and source code
- Serves as a portfolio piece for job applications

## 📁 Files

- `index.html` - Main portfolio page
- `styles.css` - Styling and responsive design
- `script.js` - Interactive features and animations
- `README.md` - This file

## 📂 Project Structure

This `docs/` folder is part of the main project repository:

```
RAG-Powered Educational Content Generator/
├── backend/                    # FastAPI backend
├── frontend/                   # Streamlit frontend
├── docs/                       # This portfolio website (GitHub Pages)
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   └── README.md
├── project_documentation/       # Project documentation
│   └── DELIVERABLES.md         # Complete project deliverables
├── README.md                   # Main project README
├── RUN.md                      # Quick start guide
└── SETUP_STEPS.md              # Detailed setup instructions
```

## 🚀 Deployment to GitHub Pages

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it something like: `rag-educational-portfolio` or `my-portfolio`
3. Make it public (required for free GitHub Pages)
4. Initialize with README (optional)

### Step 2: Upload Portfolio Files

**Option A: If deploying from main repository (recommended)**
- The `docs/` folder is already in your main repository
- Simply enable GitHub Pages and select `/docs` folder as source

**Option B: Separate repository**

```bash
# Navigate to your docs directory
cd docs

# Initialize git (if not already)
git init

# Add files
git add index.html styles.css script.js README.md

# Commit
git commit -m "Initial portfolio commit"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/rag-educational-portfolio.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Scroll down to **Pages** section (left sidebar)
4. Under **Source**, select:
   - Branch: `main`
   - Folder: `/ (root)` or `/docs` (if files are in docs folder)
5. Click **Save**
6. Your site will be available at: `https://yourusername.github.io/repository-name/`

### Step 4: Customize Content

Before deploying, update these in `index.html`:

1. **GitHub Repository Link:**
   ```html
   <a href="https://github.com/yourusername/RAG-Powered-Educational-Content-Generator">
   ```
   Replace `yourusername` with your actual GitHub username

2. **Live Demo URL:**
   ```html
   <a href="https://your-app-url.onrender.com">
   ```
   Replace with your actual deployment URL (Render, Railway, etc.)

3. **Contact Information:**
   - Already updated with: Linata Deshmukh & Pranesh Kannan
   - Add LinkedIn, GitHub links if desired

4. **Screenshots/Demos:**
   - Add screenshots of your application
   - Create a `images/` folder in `docs/`
   - Add images to showcase features
   - Update HTML to reference these images

## 🎨 Customization

### Colors
Edit `styles.css` to change the color scheme:
```css
:root {
    --primary-color: #6366f1;  /* Change this */
    --secondary-color: #8b5cf6;
    --accent-color: #ec4899;
}
```

### Content
- Update project descriptions
- Add more features
- Include screenshots
- Add video demos (embed YouTube/Vimeo)

### Add Screenshots Section

Add this to `index.html` after the Demo section:

```html
<section class="section">
    <div class="container">
        <h2 class="section-title">Screenshots</h2>
        <div class="screenshots-grid">
            <img src="images/upload-page.png" alt="Upload Page">
            <img src="images/chat-interface.png" alt="Chat Interface">
            <img src="images/competitive-quiz.png" alt="Competitive Quiz">
        </div>
    </div>
</section>
```

## 📝 What to Include

### Essential Sections:
1. ✅ Project Overview
2. ✅ Key Features
3. ✅ Technology Stack
4. ✅ Architecture Diagram
5. ✅ Technical Highlights
6. ✅ Live Demo Link
7. ✅ GitHub Repository Link

### Optional Additions:
- Screenshots/GIFs
- Video walkthrough
- Technical challenges and solutions
- Performance metrics
- Future enhancements
- Testimonials (if any)

## 🔗 Linking to Your Project

### Option 1: Link to Live Deployment
If you deploy your app on Render/Railway/etc., link to that URL.

### Option 2: Link to GitHub Repository
If not deployed, link directly to your GitHub repo with instructions.

### Option 3: Add Screenshots + Video
Show the application through screenshots and a video demo.

## 💡 Tips for Portfolio

1. **Be Specific**: Mention exact technologies, algorithms, and achievements
2. **Show Impact**: Highlight what makes your project unique
3. **Visual Appeal**: Use screenshots, diagrams, and good design
4. **Technical Depth**: Show you understand the technologies, not just used them
5. **Problem Solving**: Mention challenges you overcame
6. **Code Quality**: Link to well-organized GitHub repository

## 🎓 For Your Assignment

This portfolio demonstrates:
- ✅ Professional presentation skills
- ✅ Ability to explain technical concepts
- ✅ Understanding of the project's value
- ✅ Technical communication skills
- ✅ Web development skills (HTML/CSS/JS)

## 📱 Mobile Responsive

The portfolio is fully responsive and works on:
- Desktop
- Tablet
- Mobile devices

## 🚀 Quick Deploy

1. Push files to GitHub
2. Enable GitHub Pages in Settings
3. Wait 1-2 minutes for deployment
4. Visit your site at `https://username.github.io/repo-name`

---

## 📚 Related Documentation

- **[DELIVERABLES.md](../project_documentation/DELIVERABLES.md)** - Complete project deliverables and documentation
- **[README.md](../README.md)** - Main project overview and setup
- **[SETUP_STEPS.md](../SETUP_STEPS.md)** - Detailed setup instructions
- **[RUN.md](../RUN.md)** - Quick start guide

---

**Note**: This portfolio showcases your project. The actual application needs to be deployed separately (Render, Railway, etc.) as it requires server-side Python execution. The portfolio website itself can be hosted on GitHub Pages for free.

