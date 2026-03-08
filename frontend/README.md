# Project Argus Frontend - Deployment Guide

React frontend for AI-Powered Rental Scam Detection

## Architecture

- **Framework**: React + Vite
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Hosting**: AWS Amplify
- **API**: FastAPI backend on App Runner

## Prerequisites

1. AWS Account
2. GitHub account
3. Backend deployed on App Runner (get the URL)

## Local Development

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Update `.env` with your backend URL:
```
VITE_API_URL=http://localhost:8080
```

4. Start development server:
```bash
npm run dev
```

5. Open http://localhost:3000

## Deployment Steps

### Step 1: Get Backend URL

From App Runner deployment, copy your backend URL:
```
https://xxxxx.ap-south-1.awsapprunner.com
```

### Step 2: Push Frontend to GitHub

```bash
git init
git add .
git commit -m "Initial commit - Project Argus Frontend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/project-argus-frontend.git
git push -u origin main
```

### Step 3: Deploy to AWS Amplify

1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify)
2. Click "New app" → "Host web app"
3. **Connect repository**:
   - Select GitHub
   - Authorize AWS Amplify
   - Choose repository: `project-argus-frontend`
   - Branch: `main`

4. **Build settings**:
   - Amplify will auto-detect `amplify.yml`
   - Verify the configuration looks correct

5. **Environment variables**:
   - Click "Advanced settings"
   - Add environment variable:
     ```
     Key: VITE_API_URL
     Value: https://YOUR_APP_RUNNER_URL
     ```
   - **Important**: Use your actual App Runner URL (no trailing slash)

6. **Review and deploy**:
   - Click "Save and deploy"
   - Wait 3-5 minutes for build to complete

### Step 4: Get Amplify URL

After deployment:
1. Copy the Amplify app URL (e.g., `https://main.xxxxx.amplifyapp.com`)
2. Test the application
3. Share the URL!

## Testing the Deployment

1. Open your Amplify URL
2. Try the demo listings:
   - Click "Try a Scam Listing"
   - Click "Analyze Listing"
   - Verify the analysis results appear

3. Test custom listing:
   - Fill in the form manually
   - Upload an image (optional)
   - Submit and verify results

## Updating the Deployment

Any push to the `main` branch will trigger automatic deployment:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Amplify will automatically:
1. Pull the latest code
2. Run `npm install`
3. Run `npm run build`
4. Deploy the new version

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| VITE_API_URL | Backend API URL | https://xxxxx.ap-south-1.awsapprunner.com |

## Build Configuration

The `amplify.yml` file configures:
- **preBuild**: `npm install`
- **build**: `npm run build`
- **artifacts**: `dist/` directory
- **cache**: `node_modules/`

## Troubleshooting

### Issue: API calls failing
**Solution**: 
1. Check VITE_API_URL is set correctly in Amplify environment variables
2. Verify backend is running (visit backend URL)
3. Check browser console for CORS errors

### Issue: Build failing
**Solution**:
1. Check Amplify build logs
2. Verify `package.json` dependencies
3. Test build locally: `npm run build`

### Issue: Environment variable not working
**Solution**:
1. Ensure variable name starts with `VITE_`
2. Redeploy after adding environment variables
3. Clear browser cache

### Issue: Blank page after deployment
**Solution**:
1. Check browser console for errors
2. Verify `dist/` folder is being deployed
3. Check Amplify build logs for errors

## Custom Domain (Optional)

1. Go to Amplify Console → Domain management
2. Click "Add domain"
3. Enter your domain name
4. Follow DNS configuration steps
5. Wait for SSL certificate provisioning

## Monitoring

- **Build logs**: Amplify Console → Build history
- **Access logs**: CloudWatch Logs
- **Performance**: Amplify Console → Monitoring

## Cost Estimation

AWS Amplify Free Tier:
- Build minutes: 1000 minutes/month free
- Hosting: 15 GB served/month free
- Storage: 5 GB free

Typical costs after free tier:
- ~$0.01 per build minute
- ~$0.15 per GB served
- ~$0.023 per GB stored

## Performance Optimization

The app is optimized with:
- Vite for fast builds
- Code splitting
- Lazy loading
- Tailwind CSS purging
- Framer Motion tree-shaking

## Security

- API calls use HTTPS
- No sensitive data stored in frontend
- Environment variables for configuration
- CORS handled by backend

## Support

For issues:
1. Check Amplify build logs
2. Verify environment variables
3. Test backend API directly
4. Check browser console for errors

## Demo

Live demo: [Your Amplify URL]

Try these demo listings:
- 🚨 Scam Listing - See high risk detection
- ⚠️ Suspicious Listing - See moderate risk
- ✅ Genuine Listing - See low risk score
