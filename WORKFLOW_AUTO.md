# WORKFLOW_AUTO.md - Automated Workflow for Processing Briefing Files

## Overview
This workflow defines the automated process for handling briefing files (e.g., trending.md) as requested by the user.

## Steps for Processing GitHub Trending Chinese Briefing Files

1. **Generate Chinese Briefing**
   - Run the script to fetch GitHub Trending projects: `node generate_github_briefing.js`
   - This creates a Markdown file `github_trending_zh.md` with Chinese formatted briefing
   - Ensure Chrome is installed at `/usr/bin/google-chrome-stable` (already available in Codespaces)

2. **Upload to GitHub Repository**
   - Add the briefing file `github_trending_zh.md` to the local Git repository
   - Commit with appropriate message (e.g., "Update GitHub trending Chinese briefing")
   - Push to the remote repository: `https://github.com/sjf2525/openclaw.git`
   - Ensure Git user is configured (already set in Codespaces)

3. **Clean Up Local Workspace**
   - Delete the briefing file from the current workspace directory after successful push
   - Example: `rm github_trending_zh.md`
   - Optional: keep `generate_github_briefing.js` for future use

4. **Remove Chrome Installer File (if exists)**
   - Delete the Google Chrome installer file if it exists:
     - Location: `/workspaces/openclaw/google-chrome-stable_current_amd64.deb`
   - Example: `rm /workspaces/openclaw/google-chrome-stable_current_amd64.deb`

5. **Verification**
   - Confirm file has been pushed to GitHub
   - Confirm local files have been removed
   - Log the operation for tracking

## Automation Notes
- This workflow should be triggered whenever a briefing file needs to be processed
- The process can be implemented as a script or manual steps following this guide
- Future enhancements: create a shell script to automate all steps

## Git Configuration (Already Set)
- User: sjf2525
- Email: 40140075+sjf2525@users.noreply.github.com
- Remote: origin -> https://github.com/sjf2525/openclaw.git

## Last Execution
- 2026-02-19 13:39 UTC: Successfully processed trending.md
  - File uploaded to GitHub repository
  - Local trending.md deleted
  - Chrome installer deleted from /workspaces/openclaw/

- 2026-02-19 14:05 UTC: Successfully processed GitHub Trending Chinese briefing
  - Generated `github_trending_zh.md` with Chinese formatted briefing
  - File uploaded to GitHub repository (commit a9efb26)
  - Local `github_trending_zh.md` deleted
  - Chrome installer already removed (no action needed)