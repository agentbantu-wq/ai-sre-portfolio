# GitLab Contributors Hackathon - Cookie Session Guide

## 🚀 Quick Start

You now have an interactive tool that uses your Chrome browser cookies to access GitLab with your authenticated session!

### Prerequisites
- Chrome browser installed with GitLab login cookies
- CHROME_USER_DATA_DIR configured in `.env` file (already done: `/home/dj/.config/google-chrome/Default`)

### Run the Interactive Tool

```bash
cd /home/dj/VSCode/ai-sre-portfolio/builds/hackathon-tracker
python gitlab_interactive.py
```

### What You Can Do

The interactive tool gives you access to:

1. **View Hackathon Page** - Latest hackathon info (April 16-23, 2026)
2. **Open Your Profile** - View your contribution points and achievements
3. **Find Issues** - Discover "quick-win" issues to contribute
4. **View Leaderboard** - See current rankings and top contributors
5. **Check Authentication** - Verify your GitLab login status
6. **Browser Session** - Keep browser open for real-time work

### How Your Cookies Work

Your Chrome profile contains:
- **GitLab login credentials** (cookies/session tokens)
- **Preferences and settings**
- **History and saved data**

The tool uses this authenticated session to:
- ✅ Access your private profile
- ✅ View your contribution history
- ✅ See personalized issue recommendations
- ✅ Track your hackathon progress
- ✅ Access features that require login

### Typical Workflow

```
1. Run gitlab_interactive.py
2. Verify you're logged in (Option 5)
3. Find issues to work on (Option 3)
4. Copy the issue link
5. Keep browser open to work on issues (Option 6)
6. Your contributions auto-sync with leaderboard
```

### Tips for the Hackathon

- **Start with quick-win issues**: Look for issues with clear requirements
- **Small contributions count**: Even documentation or typo fixes earn points
- **Merge early**: MRs merged during hackathon count for prizes
- **Track your progress**: Use Option 4 to see your leaderboard rank
- **Get help**: Visit https://contributors.gitlab.com/docs/user-guide

### Key Dates

- **Starts**: April 16, 2026
- **Ends**: April 23, 2026
- **Total duration**: 1 week
- **Prizes**: SwagBundle, GitLab credits, profile achievements

### Troubleshooting

**Browser won't open:**
  - Make sure Chrome is not already running in that profile
  - Check CHROME_USER_DATA_DIR path is correct

**Not logged in:**
  - Open browser (Option 6)
  - Navigate to https://gitlab.com
  - Log in if needed
  - Restart the tool

**Cookie issues:**
  - Cookies are automatically loaded from your Chrome profile
  - No manual cookie management needed
  - Your GitLab session is persistent

### Environment Variables

Edit `.env` file to configure:
```
CHROME_USER_DATA_DIR=/home/dj/.config/google-chrome/Default
HOURLY_RATE=50
```

---

**Ready to participate? Run `python gitlab_interactive.py` now!** 🎉
