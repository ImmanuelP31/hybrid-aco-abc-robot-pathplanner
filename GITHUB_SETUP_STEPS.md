# 📋 Steps to Put This on GitHub

Follow these steps in order. Shouldn't take more than 10 minutes.

---

## Step 1 — Copy the project to your Desktop

The project folder is called `hybrid-aco-abc-robot-pathplanner`.
Move/copy it to your Desktop:

**Mac:**
```
~/Desktop/hybrid-aco-abc-robot-pathplanner/
```

**Windows:**
```
C:\Users\YourName\Desktop\hybrid-aco-abc-robot-pathplanner\
```

---

## Step 2 — Make sure Git is installed

Open a terminal (or Command Prompt on Windows) and type:
```bash
git --version
```

If it says something like `git version 2.x.x` → you're good.  
If not → download it from https://git-scm.com/downloads

---

## Step 3 — Set up Git in the project folder

Open terminal and navigate to the project:

```bash
cd ~/Desktop/hybrid-aco-abc-robot-pathplanner
```

Initialize a git repository:
```bash
git init
```

---

## Step 4 — Create a repo on GitHub

1. Go to https://github.com
2. Click the **+** button (top right) → **New repository**
3. Name it: `hybrid-aco-abc-robot-pathplanner`
4. Set it to **Public** (so people can find it)
5. **Do NOT** check "Add a README" — we already have one
6. Click **Create repository**

GitHub will show you a page with setup instructions. You'll need the repo URL — looks like:
```
https://github.com/YOUR_USERNAME/hybrid-aco-abc-robot-pathplanner.git
```

---

## Step 5 — Stage and commit everything

Back in your terminal (inside the project folder):

```bash
# Stage all files
git add .

# Commit with a message
git commit -m "Initial commit: Hybrid ACO-ABC robot path planner"
```

---

## Step 6 — Connect to GitHub and push

```bash
# Point your local repo to GitHub
git remote add origin https://github.com/YOUR_USERNAME/hybrid-aco-abc-robot-pathplanner.git

# Set the main branch name
git branch -M main

# Push everything up
git push -u origin main
```

It'll ask for your GitHub username and password.  
> ⚠️ Note: GitHub no longer accepts your password directly — you need a **Personal Access Token**.  
> Go to: Settings → Developer Settings → Personal Access Tokens → Generate new token  
> Give it "repo" scope. Use that token as your password when prompted.

---

## Step 7 — Verify it's live

Go to:
```
https://github.com/YOUR_USERNAME/hybrid-aco-abc-robot-pathplanner
```

You should see all your files and the nicely formatted README. 🎉

---

## Step 8 (Optional) — Add a demo GIF

Run the project locally, take a screen recording of the matplotlib plots,
convert to GIF (use ezgif.com or any tool), save it as `assets/demo.gif`,
then:

```bash
git add assets/demo.gif
git commit -m "Add demo GIF"
git push
```

Then update README.md to display it:
```markdown
![Demo](assets/demo.gif)
```

---

## Step 9 (Optional) — Add topics/tags to your repo

On GitHub, on your repo page, click the gear ⚙️ next to "About" and add topics:

```
python, swarm-intelligence, ant-colony-optimization, artificial-bee-colony,
robot-path-planning, metaheuristics, optimization, robotics
```

This helps people find your project when searching GitHub.

---

## Folder structure before you push

Make sure your Desktop folder looks like this:

```
hybrid-aco-abc-robot-pathplanner/
├── src/
│   ├── __init__.py
│   ├── aco.py
│   ├── abc_algo.py
│   ├── hybrid.py
│   ├── environment.py
│   ├── fitness.py
│   └── visualizer.py
├── docs/
│   └── paper_summary.md
├── results/          ← empty folder, gets filled when you run main.py
├── assets/           ← put your demo GIF here
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Common issues

**"Permission denied" on push:**  
Use a Personal Access Token (see Step 6 note above).

**"Remote origin already exists":**
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/hybrid-aco-abc-robot-pathplanner.git
```

**"Nothing to commit":**  
Did you save all your files? Run `git status` to see what Git sees.

**Matplotlib not showing plots on Mac:**  
Try adding `import matplotlib; matplotlib.use('TkAgg')` at the top of main.py.

---

That's it. Your research implementation is now on GitHub and citable. 🚀
