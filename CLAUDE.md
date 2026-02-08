
# Project Deployment Information

## Railway Deployment
- **Project Name:** sublime-empathy
- **Environment:** production

### Services
| Service | Purpose | URL Pattern |
|---------|---------|-------------|
| mindful-luck | Frontend (React/Vite) | mindful-luck-production.up.railway.app |
| urban-fortnight | Backend (FastAPI) | urban-fortnight-production.up.railway.app |

### Useful Commands
```bash
# Get backend logs
railway link --project sublime-empathy
railway service link urban-fortnight
railway logs

# Get frontend logs  
railway service link mindful-luck
railway logs
```
