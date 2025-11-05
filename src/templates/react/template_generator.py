"""
React Frontend Template Generator

This module generates React application templates with cloud-agnostic configurations
for both AWS and Azure deployments.
"""

import os
import json
from typing import Dict, List, Any
from dataclasses import dataclass

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ReactTemplateConfig:
    """Configuration for React template generation."""
    app_name: str
    cloud_provider: str
    api_endpoint: str
    authentication_enabled: bool = True
    pwa_enabled: bool = True
    typescript_enabled: bool = True
    testing_framework: str = "jest"
    ui_framework: str = "material-ui"


class ReactTemplateGenerator:
    """
    Generates React application templates with cloud-agnostic configurations.
    """
    
    def __init__(self):
        self.template_base_path = os.path.dirname(__file__)
    
    def generate_template(self, config: ReactTemplateConfig) -> Dict[str, str]:
        """
        Generate a complete React application template.
        """
        try:
            template_files = {}
            
            # Generate package.json
            template_files["package.json"] = self._generate_package_json(config)
            
            # Generate main App component
            template_files["src/App.tsx"] = self._generate_app_component(config)
            
            # Generate index.html
            template_files["public/index.html"] = self._generate_index_html(config)
            
            # Generate environment configuration
            template_files[".env.example"] = self._generate_env_config(config)
            
            # Generate cloud-specific configurations
            if config.cloud_provider.lower() == "aws":
                template_files.update(self._generate_aws_config(config))
            elif config.cloud_provider.lower() == "azure":
                template_files.update(self._generate_azure_config(config))
            
            # Generate service layer
            template_files["src/services/api.ts"] = self._generate_api_service(config)
            
            # Generate authentication components
            if config.authentication_enabled:
                template_files.update(self._generate_auth_components(config))
            
            # Generate utility files
            template_files.update(self._generate_utility_files(config))
            
            # Generate testing files
            template_files.update(self._generate_test_files(config))
            
            # Generate build and deployment configurations
            template_files.update(self._generate_build_config(config))
            
            logger.info("React template generated successfully", 
                       app_name=config.app_name, 
                       files_count=len(template_files))
            
            return template_files
            
        except Exception as e:
            logger.error("Failed to generate React template", error=str(e))
            raise
    
    def _generate_package_json(self, config: ReactTemplateConfig) -> str:
        """Generate package.json with appropriate dependencies."""
        dependencies = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.8.0",
            "axios": "^1.3.0",
            "@emotion/react": "^11.10.5",
            "@emotion/styled": "^11.10.5"
        }
        
        dev_dependencies = {
            "@types/react": "^18.0.27",
            "@types/react-dom": "^18.0.10",
            "@vitejs/plugin-react": "^3.1.0",
            "vite": "^4.1.0",
            "typescript": "^4.9.3",
            "eslint": "^8.34.0",
            "@typescript-eslint/eslint-plugin": "^5.52.0",
            "@typescript-eslint/parser": "^5.52.0"
        }
        
        scripts = {
            "dev": "vite",
            "build": "tsc && vite build",
            "preview": "vite preview",
            "lint": "eslint src --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
            "test": "vitest"
        }
        
        # Add cloud-specific dependencies
        if config.cloud_provider.lower() == "aws":
            dependencies.update({
                "aws-amplify": "^5.0.0",
                "@aws-amplify/ui-react": "^4.0.0",
                "aws-sdk": "^2.1300.0"
            })
        elif config.cloud_provider.lower() == "azure":
            dependencies.update({
                "@azure/msal-react": "^1.5.0",
                "@azure/msal-browser": "^2.35.0",
                "@azure/storage-blob": "^12.13.0"
            })
        
        # Add UI framework dependencies
        if config.ui_framework == "material-ui":
            dependencies.update({
                "@mui/material": "^5.11.0",
                "@mui/icons-material": "^5.11.0"
            })
        
        # Add testing dependencies
        if config.testing_framework == "jest":
            dev_dependencies.update({
                "vitest": "^0.28.0",
                "@testing-library/react": "^13.4.0",
                "@testing-library/jest-dom": "^5.16.5",
                "@testing-library/user-event": "^14.4.3"
            })
        
        package_json = {
            "name": config.app_name.lower().replace(" ", "-"),
            "private": True,
            "version": "0.1.0",
            "type": "module",
            "scripts": scripts,
            "dependencies": dependencies,
            "devDependencies": dev_dependencies,
            "eslintConfig": {
                "extends": [
                    "react-app",
                    "react-app/jest"
                ]
            }
        }
        
        return json.dumps(package_json, indent=2)
    
    def _generate_app_component(self, config: ReactTemplateConfig) -> str:
        """Generate main App component."""
        auth_import = ""
        auth_provider = ""
        auth_provider_close = ""
        
        if config.authentication_enabled:
            if config.cloud_provider.lower() == "aws":
                auth_import = """
import { Authenticator } from '@aws-amplify/ui-react';
import { Amplify } from 'aws-amplify';
import awsExports from './aws-exports';"""
                auth_provider = "<Authenticator.Provider>"
                auth_provider_close = "</Authenticator.Provider>"
            elif config.cloud_provider.lower() == "azure":
                auth_import = """
import { MsalProvider } from '@azure/msal-react';
import { msalInstance } from './services/auth';"""
                auth_provider = "<MsalProvider instance={msalInstance}>"
                auth_provider_close = "</MsalProvider>"
        
        ui_imports = ""
        if config.ui_framework == "material-ui":
            ui_imports = """
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';"""
        
        return f'''import React from 'react';
import {{ BrowserRouter as Router, Routes, Route }} from 'react-router-dom';{auth_import}{ui_imports}
import './App.css';

// Components
import Header from './components/Header';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';

// Services
import {{ ApiProvider }} from './services/api';

{f"Amplify.configure(awsExports);" if config.cloud_provider.lower() == "aws" and config.authentication_enabled else ""}
{f"const theme = createTheme();" if config.ui_framework == "material-ui" else ""}

function App() {{
  return (
    {auth_provider}
      {f"<ThemeProvider theme={{theme}}>" if config.ui_framework == "material-ui" else ""}
        {f"<CssBaseline />" if config.ui_framework == "material-ui" else ""}
        <ApiProvider>
          <Router>
            <div className="App">
              <Header />
              {f"<Container maxWidth='lg'>" if config.ui_framework == "material-ui" else "<main>"}
                <Routes>
                  <Route path="/" element={{<Home />}} />
                  <Route path="/dashboard" element={{<Dashboard />}} />
                  <Route path="/profile" element={{<Profile />}} />
                </Routes>
              {f"</Container>" if config.ui_framework == "material-ui" else "</main>"}
            </div>
          </Router>
        </ApiProvider>
      {f"</ThemeProvider>" if config.ui_framework == "material-ui" else ""}
    {auth_provider_close}
  );
}}

export default App;'''
    
    def _generate_index_html(self, config: ReactTemplateConfig) -> str:
        """Generate index.html template."""
        pwa_manifest = ""
        pwa_meta = ""
        
        if config.pwa_enabled:
            pwa_manifest = '<link rel="manifest" href="/manifest.json" />'
            pwa_meta = '''
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Cloud-agnostic React application" />
    <link rel="apple-touch-icon" href="/logo192.png" />'''
        
        return f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />{pwa_meta}
    {pwa_manifest}
    <title>{config.app_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>'''
    
    def _generate_env_config(self, config: ReactTemplateConfig) -> str:
        """Generate environment configuration template."""
        env_vars = [
            "# API Configuration",
            "VITE_API_BASE_URL=http://localhost:3001/api",
            "VITE_APP_NAME=" + config.app_name,
            "",
            "# Cloud Provider Configuration",
            f"VITE_CLOUD_PROVIDER={config.cloud_provider.upper()}"
        ]
        
        if config.cloud_provider.lower() == "aws":
            env_vars.extend([
                "",
                "# AWS Configuration",
                "VITE_AWS_REGION=us-east-1",
                "VITE_AWS_USER_POOL_ID=your-user-pool-id",
                "VITE_AWS_USER_POOL_WEB_CLIENT_ID=your-client-id",
                "VITE_AWS_API_GATEWAY_URL=https://your-api-id.execute-api.region.amazonaws.com/prod"
            ])
        elif config.cloud_provider.lower() == "azure":
            env_vars.extend([
                "",
                "# Azure Configuration",
                "VITE_AZURE_CLIENT_ID=your-client-id",
                "VITE_AZURE_TENANT_ID=your-tenant-id",
                "VITE_AZURE_REDIRECT_URI=http://localhost:3000",
                "VITE_AZURE_API_BASE_URL=https://your-api.azurewebsites.net/api"
            ])
        
        if config.authentication_enabled:
            env_vars.extend([
                "",
                "# Authentication",
                "VITE_AUTH_ENABLED=true"
            ])
        
        return "\\n".join(env_vars)
    
    def _generate_aws_config(self, config: ReactTemplateConfig) -> Dict[str, str]:
        """Generate AWS-specific configuration files."""
        files = {}
        
        # AWS Amplify configuration
        files["src/aws-exports.ts"] = '''const awsconfig = {
  Auth: {
    region: import.meta.env.VITE_AWS_REGION,
    userPoolId: import.meta.env.VITE_AWS_USER_POOL_ID,
    userPoolWebClientId: import.meta.env.VITE_AWS_USER_POOL_WEB_CLIENT_ID,
    mandatorySignIn: true,
    authenticationFlowType: 'USER_SRP_AUTH'
  },
  API: {
    endpoints: [
      {
        name: 'api',
        endpoint: import.meta.env.VITE_AWS_API_GATEWAY_URL,
        region: import.meta.env.VITE_AWS_REGION
      }
    ]
  },
  Storage: {
    AWSS3: {
      bucket: import.meta.env.VITE_AWS_S3_BUCKET,
      region: import.meta.env.VITE_AWS_REGION
    }
  }
};

export default awsconfig;'''
        
        return files
    
    def _generate_azure_config(self, config: ReactTemplateConfig) -> Dict[str, str]:
        """Generate Azure-specific configuration files."""
        files = {}
        
        # Azure MSAL configuration
        files["src/services/auth.ts"] = '''import { PublicClientApplication } from '@azure/msal-browser';

const msalConfig = {
  auth: {
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID,
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_TENANT_ID}`,
    redirectUri: import.meta.env.VITE_AZURE_REDIRECT_URI,
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
};

export const msalInstance = new PublicClientApplication(msalConfig);

export const loginRequest = {
  scopes: ['User.Read', 'openid', 'profile'],
};'''
        
        return files
    
    def _generate_api_service(self, config: ReactTemplateConfig) -> str:
        """Generate API service layer."""
        auth_interceptor = ""
        
        if config.authentication_enabled:
            if config.cloud_provider.lower() == "aws":
                auth_interceptor = '''
// AWS Amplify auth interceptor
import { Auth } from 'aws-amplify';

api.interceptors.request.use(async (config) => {
  try {
    const token = (await Auth.currentSession()).getIdToken().getJwtToken();
    config.headers.Authorization = `Bearer ${token}`;
  } catch (error) {
    console.error('Failed to get auth token:', error);
  }
  return config;
});'''
            elif config.cloud_provider.lower() == "azure":
                auth_interceptor = '''
// Azure MSAL auth interceptor
import { msalInstance } from './auth';

api.interceptors.request.use(async (config) => {
  try {
    const accounts = msalInstance.getAllAccounts();
    if (accounts.length > 0) {
      const request = {
        scopes: ['User.Read'],
        account: accounts[0],
      };
      const response = await msalInstance.acquireTokenSilent(request);
      config.headers.Authorization = `Bearer ${response.accessToken}`;
    }
  } catch (error) {
    console.error('Failed to get auth token:', error);
  }
  return config;
});'''
        
        return f'''import axios from 'axios';
import React, {{ createContext, useContext, ReactNode }} from 'react';

// Create axios instance
const api = axios.create({{
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {{
    'Content-Type': 'application/json',
  }},
}});

{auth_interceptor}

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {{
    if (error.response?.status === 401) {{
      // Handle unauthorized access
      console.error('Unauthorized access');
    }}
    return Promise.reject(error);
  }}
);

// API service methods
export const apiService = {{
  // Users
  getUsers: () => api.get('/users'),
  getUser: (id: string) => api.get(`/users/${{id}}`),
  createUser: (userData: any) => api.post('/users', userData),
  updateUser: (id: string, userData: any) => api.put(`/users/${{id}}`, userData),
  deleteUser: (id: string) => api.delete(`/users/${{id}}`),
  
  // Health check
  healthCheck: () => api.get('/health'),
}};

// API Context for React components
interface ApiContextType {{
  api: typeof apiService;
}}

const ApiContext = createContext<ApiContextType | undefined>(undefined);

export const ApiProvider: React.FC<{{ children: ReactNode }}> = ({{ children }}) => {{
  return (
    <ApiContext.Provider value={{{{ api: apiService }}}}>
      {{children}}
    </ApiContext.Provider>
  );
}};

export const useApi = (): ApiContextType => {{
  const context = useContext(ApiContext);
  if (!context) {{
    throw new Error('useApi must be used within an ApiProvider');
  }}
  return context;
}};

export default api;'''
    
    def _generate_auth_components(self, config: ReactTemplateConfig) -> Dict[str, str]:
        """Generate authentication components."""
        files = {}
        
        if config.cloud_provider.lower() == "aws":
            files["src/components/AuthWrapper.tsx"] = '''import React from 'react';
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';

interface AuthWrapperProps {
  children: React.ReactNode;
}

const AuthWrapper: React.FC<AuthWrapperProps> = ({ children }) => {
  return (
    <Authenticator>
      {({ signOut, user }) => (
        <div>
          <nav>
            <button onClick={signOut}>Sign Out ({user?.username})</button>
          </nav>
          {children}
        </div>
      )}
    </Authenticator>
  );
};

export default AuthWrapper;'''
        
        elif config.cloud_provider.lower() == "azure":
            files["src/components/AuthWrapper.tsx"] = '''import React from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { loginRequest } from '../services/auth';

interface AuthWrapperProps {
  children: React.ReactNode;
}

const AuthWrapper: React.FC<AuthWrapperProps> = ({ children }) => {
  const { instance } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  const handleLogin = () => {
    instance.loginPopup(loginRequest);
  };

  const handleLogout = () => {
    instance.logoutPopup();
  };

  if (!isAuthenticated) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <h2>Please sign in to continue</h2>
        <button onClick={handleLogin}>Sign In</button>
      </div>
    );
  }

  return (
    <div>
      <nav>
        <button onClick={handleLogout}>Sign Out</button>
      </nav>
      {children}
    </div>
  );
};

export default AuthWrapper;'''
        
        return files
    
    def _generate_utility_files(self, config: ReactTemplateConfig) -> Dict[str, str]:
        """Generate utility files."""
        files = {}
        
        # Common utility functions
        files["src/utils/constants.ts"] = f'''export const APP_CONFIG = {{
  name: '{config.app_name}',
  version: '1.0.0',
  cloudProvider: '{config.cloud_provider.upper()}',
  authEnabled: {str(config.authentication_enabled).lower()},
}};

export const API_ENDPOINTS = {{
  USERS: '/users',
  HEALTH: '/health',
}};

export const HTTP_STATUS = {{
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
}};'''
        
        # Error handling utilities
        files["src/utils/errorHandler.ts"] = '''export interface ApiError {
  message: string;
  status?: number;
  code?: string;
}

export const handleApiError = (error: any): ApiError => {
  if (error.response) {
    return {
      message: error.response.data?.message || 'An error occurred',
      status: error.response.status,
      code: error.response.data?.code,
    };
  } else if (error.request) {
    return {
      message: 'Network error - please check your connection',
      code: 'NETWORK_ERROR',
    };
  } else {
    return {
      message: error.message || 'An unexpected error occurred',
      code: 'UNKNOWN_ERROR',
    };
  }
};

export const formatErrorMessage = (error: ApiError): string => {
  return `${error.message}${error.status ? ` (${error.status})` : ''}`;
};'''
        
        return files
    
    def _generate_test_files(self, config: ReactTemplateConfig) -> Dict[str, str]:
        """Generate test files."""
        files = {}
        
        # App component test
        files["src/App.test.tsx"] = '''import React from 'react';
import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import App from './App';

// Mock the auth service
vi.mock('./services/auth', () => ({
  msalInstance: {
    getAllAccounts: () => [],
    acquireTokenSilent: vi.fn(),
  },
}));

test('renders app component', () => {
  render(<App />);
  // Add your specific test assertions here
  expect(document.querySelector('.App')).toBeInTheDocument();
});'''
        
        # API service test
        files["src/services/api.test.ts"] = '''import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { apiService } from './api';

vi.mock('axios');
const mockedAxios = vi.mocked(axios);

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should make GET request for users', async () => {
    const mockUsers = [{ id: 1, name: 'John Doe' }];
    mockedAxios.create.mockReturnValue({
      get: vi.fn().mockResolvedValue({ data: mockUsers }),
    } as any);

    // Test would need to be adjusted based on actual implementation
    expect(apiService.getUsers).toBeDefined();
  });
});'''
        
        # Vitest configuration
        files["vitest.config.ts"] = '''import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
  },
});'''
        
        # Test setup
        files["src/setupTests.ts"] = '''import '@testing-library/jest-dom';'''
        
        return files
    
    def _generate_build_config(self, config: ReactTemplateConfig) -> Dict[str, str]:
        """Generate build and deployment configuration files."""
        files = {}
        
        # Vite configuration
        files["vite.config.ts"] = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'build',
    sourcemap: true,
  },
  server: {
    port: 3000,
    open: true,
  },
  preview: {
    port: 3000,
  },
})'''
        
        # TypeScript configuration
        if config.typescript_enabled:
            files["tsconfig.json"] = '''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}'''
            
            files["tsconfig.node.json"] = '''{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}'''
        
        # ESLint configuration
        files[".eslintrc.cjs"] = '''module.exports = {
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'eslint-config-prettier',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': 'warn',
  },
}'''
        
        # PWA manifest
        if config.pwa_enabled:
            files["public/manifest.json"] = f'''{
  "short_name": "{config.app_name}",
  "name": "{config.app_name}",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}'''
        
        return files


# Factory function
def create_react_template_generator() -> ReactTemplateGenerator:
    """Create a ReactTemplateGenerator instance."""
    return ReactTemplateGenerator()