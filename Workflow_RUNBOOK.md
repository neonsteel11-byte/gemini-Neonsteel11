# Syndicate Pipeline Runbook

## Emergency Procedures
- **Stop Automation:** Change `"paused": false` to `"paused": true` in `output/system_state.json` and push to `main`.
- **Reset Daily Cap:** Change `"uploads_today": X` back to `0` in `output/system_state.json`.

## Troubleshooting
- **Pipeline Failing?** Go to the **Actions** tab, click the failed run, and expand the "Upload to YouTube" step.
- **Auth Error:** If you get an `invalid_grant` error, your Refresh Token has expired. Regenerate it locally and update the `YT_REFRESH_TOKEN` secret in GitHub Settings.
- **Quota Exceeded:** If you hit your daily limit, the system will self-pause. Wait 24 hours or manually reset the count in `system_state.json`.