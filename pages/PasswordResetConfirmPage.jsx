import React, { useState } from 'react';
// Importamos 'useLocation' para apanhar o email e token
import { useNavigate, useLocation, Navigate } from 'react-router-dom';
import Button from '../components/Button.jsx';
import FormInput from '../components/FormInput.jsx';
import styles from './AuthForm.module.css'; // Reutilizando o CSS!
import logoUebax from "../assets/logo.png";
import { apiFetch } from '../utils/apiService.js';
import { FaLock } from 'react-icons/fa'; // Ícone de cadeado

const PasswordResetConfirmPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // 1. Apanha o e-mail E o token do ecrã anterior
  const email = location.state?.email;
  const token = location.state?.token;

  // Estados para os novos campos de senha
  const [passwords, setPasswords] = useState({
    password: '',
    password2: '', // Para a "Confirmação de Senha"
  });
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');

  // 'Handler' para atualizar os campos de senha
  const handleChange = (e) => {
    setPasswords({
      ...passwords,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // 2. Validação local (como na sua especificação)
    if (passwords.password !== passwords.password2) {
      setError('As senhas não coincidem');
      return; // Para a execução
    }
    
    setLoading(true);

    try {
      // 3. Chamar a API final (Ecrã 5 do backend)
      // Enviamos tudo: email, token e as novas senhas
      await apiFetch('/password-reset/confirm/', {
        method: 'POST',
        skipAuth: true,
        body: JSON.stringify({
          email: email,
          token: token,
          password: passwords.password,
          password2: passwords.password2,
        }),
      });
      
      // 4. SUCESSO!
      setLoading(false);
      setSuccess('Sua senha foi redefinida com sucesso! A redirecionar para o login...');

      // 5. Redirecionar para o LOGIN
      setTimeout(() => {
        navigate('/login');
      }, 3000); // Espera 3 segundos

    } catch (err) {
      // 6. ERRO! (A API pode dizer "Token Inválido" ou "Senha muito fraca")
      setLoading(false);
      setError(err.message);
      console.error(err);
    }
  };

  // 7. Segurança: Se o usuário chegar aqui sem email OU token,
  // mandamo-lo de volta para o início do fluxo.
  if (!email || !token) {
    return <Navigate to="/redefinir-senha" replace />;
  }

  return (
    <div className={styles.pageContainer}>
      <img src={logoUebax} alt="Logo UEBAX" className={styles.logo} />

      <h2 className={styles.authTitle}>Nova Senha</h2>
      
      <form className={styles.loginForm} onSubmit={handleSubmit}>
        
        {error && <div className={styles.errorPopup}>{error}</div>}
        {success && <div className={styles.successPopup}>{success}</div>}

        <FormInput
          label="Digite sua nova senha"
          icon={<FaLock />}
          type="password"
          name="password"
          value={passwords.password}
          onChange={handleChange}
          required={true}
        />
        <FormInput
          label="Confirme sua senha"
          icon={<FaLock />}
          type="password"
          name="password2"
          value={passwords.password2}
          onChange={handleChange}
          required={true}
        />

        <Button type="submit" variant="primary" disabled={loading}>
          {loading ? 'A guardar...' : 'Confirmar'}
        </Button>
      </form>
    </div>
  );
};

export default PasswordResetConfirmPage;