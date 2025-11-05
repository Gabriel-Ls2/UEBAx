// Em: main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import LoginPage from './pages/LoginPage.jsx';
import CadastroPage from './pages/CadastroPage.jsx';
import PasswordResetRequestPage from './pages/PasswordResetRequestPage.jsx';
import PasswordVerifyCodePage from './pages/PasswordVerifyCodePage.jsx';
import PasswordResetConfirmPage from './pages/PasswordResetConfirmPage.jsx';
import DashboardPage from './pages/DashboardPage.jsx'; 
import EventosPage from './pages/EventosPage.jsx';
import AlertasPage from './pages/AlertasPage.jsx';
import ProtectedRoute from './utils/ProtectedRoute.jsx';
import DashboardLayout from './layouts/DashboardLayout.jsx';
import './index.css';

// NOVO: Define nossas "rotas" (as URLs do app)
const router = createBrowserRouter([
  {
    path: '/',
    element: <LoginPage />, 
  },
  {
    path: '/login', 
    element: <LoginPage />,
  },
  {
    path: '/cadastro', 
    element: <CadastroPage />,
  },
  {
    path: '/redefinir-senha', 
    element: <PasswordResetRequestPage />,
  },
  {
    path: '/verificar-codigo', 
    element: <PasswordVerifyCodePage />,
  },
  {
    path: '/nova-senha', 
    element: <PasswordResetConfirmPage />,
  },
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <DashboardLayout />
      </ProtectedRoute>
    ),
    // 'children' são as "páginas filhas" que abrem DENTRO do <Outlet />
    children: [
      {
        index: true, 
        element: <DashboardPage />, 
      },
      {
        path: 'eventos', 
        element: <EventosPage />, 
      },
      {
        path: 'alertas', 
        element: <AlertasPage />,
      },
    ],
  },
]);

// NOVO: Diz ao React para usar o Roteador
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);