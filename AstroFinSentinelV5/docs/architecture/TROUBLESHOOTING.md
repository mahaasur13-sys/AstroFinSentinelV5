# Troubleshooting Guide

## Dashboard Shows "No Data"
1. Check sessions: ls data/meta_rl/sessions/
2. Run evolution: Dashboard → Evolution → Start Evolution
3. Check logs: tail -f /tmp/dash.log

## Ollama Not Responding
curl http://localhost:11434/api/tags
systemctl restart ollama

## Docker Container Crash Loop
docker logs astrofin_app --tail 50
docker exec astrofin_app supervisorctl status

## Git Permission Error
git remote set-url origin https://ghp_YOUR_TOKEN@github.com/mahaasur13-sys/AstroFinSentinelV5.git
