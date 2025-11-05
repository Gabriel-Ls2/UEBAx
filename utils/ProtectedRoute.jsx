import React from 'react';
import { Navigate } from 'react-router-dom';

/**
 * O nosso "Porteiro".
 * Este componente verifica se o usuário está logado (tem um token).
 * Se sim, ele "renderiza" (mostra) a página que lhe foi passada (os 'children').
 * Se não, ele "redireciona" o usuário para a página de login.
 */
const ProtectedRoute = ({ children }) => {
  // 1. Verifica no localStorage se o "crachá" (accessToken) existe
  const token = localStorage.getItem('accessToken');

  if (!token) {
    // 2. Não tem token? Redireciona para /login
    return <Navigate to="/login" replace />;
  }

  // 3. Tem token? Deixa o usuário ver a página (os 'children')
  return children;
};

export default ProtectedRoute;