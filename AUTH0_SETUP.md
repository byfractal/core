# Auth0 Authentication Setup

This guide explains how to set up and configure Auth0 authentication for the application.

## Prerequisites

1. An Auth0 account (you can sign up at [https://auth0.com](https://auth0.com))
2. The backend application set up locally

## Auth0 Configuration

### 1. Create an Auth0 Application

1. Log in to your Auth0 dashboard
2. Go to "Applications" > "Applications"
3. Click "Create Application"
4. Enter a name for your application (e.g., "My API Application")
5. Select "Regular Web Applications"
6. Click "Create"

### 2. Configure Application Settings

1. In your new application, go to the "Settings" tab
2. Configure the following:
   - **Allowed Callback URLs**: `http://localhost:8000/api/auth/callback` (for local development)
   - **Allowed Logout URLs**: `http://localhost:3000`
   - **Allowed Web Origins**: `http://localhost:3000`
   - **Allowed Origins (CORS)**: `http://localhost:3000`
3. Scroll down and click "Save Changes"

### 3. Create an API

1. Go to "Applications" > "APIs"
2. Click "Create API"
3. Enter:
   - **Name**: Your API name (e.g., "My API")
   - **Identifier**: A URL-like identifier (e.g., `https://api.yourdomain.com`)
   - **Signing Algorithm**: RS256
4. Click "Create"

### 4. Configure API Permissions (Scopes)

1. In your new API, go to the "Permissions" tab
2. Add permissions like:
   - `read:admin` - Access to admin features
   - `read:feedback` - Access to read feedback data
   - `write:feedback` - Permission to create/update feedback data
3. Click "Add"

## Backend Configuration

### 1. Environment Variables

Copy the `.env.example` file to `.env` and update the Auth0 variables:

```
# Auth0 Configuration
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_API_AUDIENCE=https://your-api-identifier
AUTH0_CALLBACK_URL=http://localhost:8000/api/auth/callback
USE_AUTH0=true
```

- `AUTH0_DOMAIN`: Your Auth0 tenant domain (from Application Settings)
- `AUTH0_CLIENT_ID`: Client ID from your Auth0 Application
- `AUTH0_CLIENT_SECRET`: Client Secret from your Auth0 Application
- `AUTH0_API_AUDIENCE`: API Identifier you created
- `AUTH0_CALLBACK_URL`: Callback URL for Auth0 redirects

### 2. Frontend Configuration

If you have a frontend application, you'll need to configure it to use Auth0 as well. The basic flow is:

1. Redirect users to the login URL from `/api/auth/login`
2. Handle the callback at your frontend's `/auth-callback` route
3. Store the tokens and use them for authenticated API requests

## Using the Auth0 Authentication

### Authentication Flow

1. Users are redirected to Auth0's Universal Login screen
2. After authentication, Auth0 redirects back to your application with an authorization code
3. Your backend exchanges this code for access and ID tokens
4. The tokens are passed to the frontend for storage and future API calls

### API Routes

The following routes are available for Auth0 authentication:

- `GET /api/auth/login`: Redirects to Auth0 login page
- `GET /api/auth/callback`: Handles Auth0 callback after authentication
- `GET /api/auth/profile`: Returns user profile (requires authentication)
- `GET /api/auth/admin`: Admin-only route (requires `read:admin` permission)
- `GET /api/auth/public`: Public route (no authentication required)

### Protecting Routes

To protect routes in your API:

1. For simple authentication:
   ```python
   @app.get("/some-protected-route")
   @requires_auth
   async def protected_route(current_user: Auth0User = Depends(get_current_user)):
       return {"message": f"Hello, {current_user.name}!"}
   ```

2. For routes requiring specific permissions:
   ```python
   @app.get("/admin-route")
   @requires_scopes(["read:admin"])
   async def admin_route(current_user: Auth0User = Depends(get_current_user)):
       return {"message": "Admin access granted"}
   ```

## Troubleshooting

### Common Issues

1. **Invalid token errors**: Check that your `AUTH0_DOMAIN` and `AUTH0_API_AUDIENCE` match exactly with your Auth0 settings
2. **CORS errors**: Ensure your Auth0 application has the correct Allowed Origins settings
3. **Callback errors**: Verify that your callback URL is correctly registered in Auth0 and matches your `.env` configuration

### Testing Authentication

You can test your Auth0 integration by:

1. Accessing `/api/auth/login` in your browser
2. Completing the Auth0 login process
3. Being redirected back to your application
4. Accessing protected endpoints like `/api/auth/profile`

## Additional Resources

- [Auth0 Documentation](https://auth0.com/docs)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Auth0 Python SDK](https://github.com/auth0/auth0-python) 