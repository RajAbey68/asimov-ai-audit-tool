# Publishing ASIMOV AI Audit Tool to GitHub

This guide will walk you through publishing your ASIMOV AI Governance Audit Tool source code to GitHub.

---

## Prerequisites

✅ **.gitignore created** - Protects sensitive data  
✅ **README.md updated** - Comprehensive project documentation  
✅ **Documentation complete** - Executive Summary, Technical Design, API Reference  

---

## Option 1: Using Replit's Git Pane (Recommended)

### Step 1: Open the Git Pane
1. In your Replit workspace, look for the **Git icon** in the left sidebar (looks like a branch icon)
2. Click to open the Git pane

### Step 2: Create a GitHub Repository
1. Go to [GitHub.com](https://github.com)
2. Click the **"+"** icon in the top-right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `asimov-ai-audit-tool` (or your preferred name)
   - **Description**: "Enterprise AI Governance Audit Tool - 251 controls across EU AI Act, NIST AI RMF, ISO/IEC, GDPR, SCF"
   - **Visibility**: Choose **Public** or **Private**
   - **DON'T** initialize with README (we already have one)
5. Click **"Create repository"**

### Step 3: Connect Replit to GitHub
1. In the Git pane, you should see an option to **"Connect to GitHub"** or **"Initialize repository"**
2. Follow the prompts to authenticate with GitHub
3. Select your newly created repository

### Step 4: Stage and Commit Files
1. In the Git pane, you'll see all your files listed
2. Click **"Stage all"** or individually select files to commit:
   - ✅ All Python files (app.py, bulletproof_startup.py, etc.)
   - ✅ Documentation (README.md, ASIMOV_*.md)
   - ✅ Templates (templates/ folder)
   - ✅ .gitignore
   - ❌ **DON'T commit**: audit_controls.db, evidence_files/, *.log files (already in .gitignore)
3. Write a commit message: `Initial commit: ASIMOV AI Governance Audit Tool v1.0`
4. Click **"Commit"**

### Step 5: Push to GitHub
1. Click the **"Push"** button in the Git pane
2. Your code will be pushed to GitHub
3. Visit your repository on GitHub to verify

---

## Option 2: Using Shell/Terminal Commands

If you prefer using Git commands in the Replit Shell:

### Step 1: Create GitHub Repository
Follow the same steps as Option 1, Step 2 above.

### Step 2: Configure Git (if needed)
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Step 3: Check Git Status
```bash
git status
```

You should see all your files listed. The .gitignore will automatically exclude sensitive files.

### Step 4: Stage All Files
```bash
git add .
```

### Step 5: Commit Changes
```bash
git commit -m "Initial commit: ASIMOV AI Governance Audit Tool v1.0"
```

### Step 6: Add GitHub Remote
Replace `yourusername` and `asimov-ai-audit-tool` with your actual GitHub username and repository name:

```bash
git remote add origin https://github.com/yourusername/asimov-ai-audit-tool.git
```

### Step 7: Push to GitHub

**Option A - Using Personal Access Token (Recommended for Private Repos):**

1. Create a GitHub Personal Access Token:
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control of private repositories)
   - Copy the token

2. Set as Replit Secret:
   - In Replit, go to **Secrets** (lock icon in sidebar)
   - Add a new secret:
     - Key: `GIT_URL`
     - Value: `https://yourusername:YOUR_TOKEN@github.com/yourusername/asimov-ai-audit-tool.git`

3. Push using the secret:
```bash
git push $GIT_URL main
```

**Option B - Using HTTPS (Will prompt for credentials):**
```bash
git push -u origin main
```

Enter your GitHub username and personal access token when prompted.

---

## What Gets Published

### ✅ Included in GitHub Repository:

**Core Application:**
- `app.py` - Main Flask application
- `bulletproof_startup.py` - Production startup
- `roadmap_management.py` - Roadmap management blueprint
- `asimov_report_dashboard.py` - Analytics dashboard
- `evidence_evaluation_engine.py` - AI evidence evaluation
- `evidence_handler.py` - Evidence file management
- All other Python modules

**Documentation:**
- `README.md` - Main project documentation
- `ASIMOV_EXECUTIVE_SUMMARY.md` - Executive overview
- `ASIMOV_TECHNICAL_DESIGN.md` - Technical architecture
- `ASIMOV_API_REFERENCE.md` - API documentation
- `GITHUB_PUBLISHING_GUIDE.md` - This guide

**Templates & Static Files:**
- `templates/` - All HTML templates
- `sector_references.json` - Regulatory references

**Configuration:**
- `.gitignore` - Git ignore rules
- `requirements.txt` - Python dependencies (if you create one)

### ❌ Excluded from GitHub (Protected by .gitignore):

**Sensitive Data:**
- `audit_controls.db` - Database with audit data
- `evidence_files/` - Uploaded evidence documents
- `.env` - Environment variables
- `*.log` - Log files

**System Files:**
- `.replit` - Replit configuration
- `replit.nix` - Nix configuration
- `__pycache__/` - Python cache
- `.upm/` - Package manager cache

---

## Post-Publishing Steps

### 1. Add Repository Description
On GitHub, edit your repository to add:
- **Description**: "Enterprise AI Governance Audit Tool - 251 controls across EU AI Act, NIST AI RMF, ISO/IEC, GDPR, SCF"
- **Topics/Tags**: `ai-governance`, `compliance-audit`, `eu-ai-act`, `nist-ai-rmf`, `flask`, `python`, `openai`, `gpt-4`
- **Website**: Your deployed URL (if you have one)

### 2. Create a requirements.txt
Generate a requirements file for easy installation:

```bash
# Create requirements.txt with all dependencies
cat > requirements.txt << 'EOF'
flask>=2.3.0
werkzeug>=2.3.0
openai>=1.0.0
pandas>=2.0.0
openpyxl>=3.0.0
python-docx>=0.8.0
pypdf2>=3.0.0
beautifulsoup4>=4.0.0
weasyprint>=59.0
python-dateutil>=2.8.0
python-dotenv>=1.0.0
requests>=2.31.0
pytest>=7.4.0
EOF

# Commit and push requirements.txt
git add requirements.txt
git commit -m "Add requirements.txt"
git push
```

### 3. Add License File (Optional)
```bash
# Create a LICENSE file (adjust based on your preference)
cat > LICENSE << 'EOF'
Proprietary License

Copyright (c) 2025 [Your Name/Organization]

All rights reserved.

This software and associated documentation files (the "Software") are proprietary 
and confidential. Unauthorized copying, modification, distribution, or use of this 
Software, via any medium, is strictly prohibited without explicit written permission 
from the copyright holder.
EOF

git add LICENSE
git commit -m "Add license"
git push
```

### 4. Set Up GitHub Pages for Documentation (Optional)
1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under "Source", select **main branch** and **/docs** or **/ (root)**
4. Your README.md will be displayed as the main page

### 5. Enable GitHub Issues
1. Go to **Settings** → **General**
2. Under "Features", check **Issues**
3. This allows users to report bugs and request features

---

## Updating Your Repository

When you make changes to your code:

**Using Git Pane:**
1. Make your changes in Replit
2. Open the Git pane
3. Stage changed files
4. Write a commit message
5. Click "Commit and Push"

**Using Shell:**
```bash
git add .
git commit -m "Description of changes"
git push
```

---

## Troubleshooting

### Problem: "Repository not found" error
**Solution:** Make sure you've created the repository on GitHub first and the URL is correct.

### Problem: Authentication failed
**Solution:** Use a GitHub Personal Access Token instead of your password:
1. Generate token: GitHub → Settings → Developer settings → Personal access tokens
2. Use token as password when prompted

### Problem: Can't push to repository
**Solution:** Check if you have write access to the repository. If it's an organization repo, ensure you have proper permissions.

### Problem: Large files rejected
**Solution:** The .gitignore already excludes large files like the database and evidence files. If you see this error, check what files are being committed:
```bash
git status
git ls-files --others --exclude-standard
```

### Problem: Conflicts when pushing
**Solution:** Pull the latest changes first:
```bash
git pull origin main
# Resolve any conflicts
git push origin main
```

---

## Security Reminders

Before pushing to GitHub, **VERIFY** that sensitive data is excluded:

✅ **Check .gitignore includes:**
- `audit_controls.db` - Database
- `evidence_files/` - Evidence uploads
- `.env` - Environment variables
- `*.log` - Log files

✅ **Never commit:**
- OpenAI API keys
- Database files with real audit data
- User-uploaded evidence files
- Secret tokens or passwords

✅ **Already protected in .gitignore:**
All sensitive files are already excluded in the .gitignore file I created.

---

## GitHub Repository URL

After publishing, your repository will be available at:

```
https://github.com/yourusername/asimov-ai-audit-tool
```

You can then share this URL with:
- Collaborators
- Stakeholders
- Open source community (if public)

---

## Next Steps

After publishing to GitHub, consider:

1. **Add GitHub Actions** - Set up CI/CD for automated testing
2. **Create Wiki** - Detailed deployment and configuration guides
3. **Add Screenshots** - Visual demos of the application
4. **Create Releases** - Tag stable versions (v1.0, v1.1, etc.)
5. **Set up Issue Templates** - Standardize bug reports and feature requests
6. **Add Contributing Guide** - Guidelines for contributors

---

## Support

If you encounter issues publishing to GitHub:
- Check Replit's [Git documentation](https://docs.replit.com/programming-ide/using-git-on-replit)
- Visit the [GitHub Help](https://help.github.com/)
- Contact Replit support

---

**Your ASIMOV AI Governance Audit Tool is ready to be shared with the world! 🚀**
