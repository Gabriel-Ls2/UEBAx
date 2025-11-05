import React, { useState } from 'react';
// NOVO: 'useLocation' para ler o e-mail que a página anterior passou
import { useNavigate, useLocation, Navigate } from 'react-router-dom';
import Button from '../components/Button.jsx';
import FormInput from '../components/FormInput.jsx';
import styles from './AuthForm.module.css'; // Reutilizando o CSS!
import logoUebax from "../assets/logo.png";
import { apiFetch } from '../utils/apiService.js';
import { FaLock } from 'react-icons/fa'; // Ícone de cadeado

const PasswordVerifyCodePage = () => {
  const navigate = useNavigate();
  const location = useLocation(); // Ativa o hook
  
  // 1. Apanha o e-mail do ecrã anterior
  // location.state pode ser 'null' se o usuário aceder ao URL diretamente
  const email = location.state?.email;

  // Estados
  const [token, setToken] = useState(''); // O código de 6 dígitos
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      // 2. Chamar a API que fizemos (Ecrã 4 do backend)
      // Enviamos o e-mail E o token
      await apiFetch('/password-reset/verify/', {
        method: 'POST',
        skipAuth: true,
        body: JSON.stringify({ email: email, token: token }),
      });
      
      // 3. SUCESSO! (A API devolveu "Token Confirmado")
      setLoading(false);
      setSuccess('Código validado! A redirecionar...');

      // 4. Redirecionar para o Ecrã 3 (Nova Senha)
      setTimeout(() => {
        // Passamos o email E o token, pois o próximo ecrã precisa de AMBOS
        navigate('/nova-senha', { 
          state: { email: email, token: token } 
        });
      }, 2000); // Espera 2 segundos

    } catch (err) {
      // 5. ERRO! (A nossa API já devolve "Token Inválido" ou "Token Expirado")
      setLoading(false);
      setError(err.message);
      console.error(err);
    }
  };

  // 6. Segurança: Se o usuário chegar a esta página sem um e-mail,
  // (ex: digitando o URL), mandamo-lo de volta para o início do fluxo.
  if (!email) {
    return <Navigate to="/redefinir-senha" replace />;
  }

  // O JSX é quase idêntico ao do Ecrã 1
  return (
    <div className={styles.pageContainer}>
      <img src={logoUebax} alt="Logo UEBAX" className={styles.logo} />

      <h2 className={styles.authTitle}>Verificação de código</h2>
      
      <form className={styles.loginForm} onSubmit={handleSubmit}>
        
        {error && <div className={styles.errorPopup}>{error}</div>}
        {success && <div className={styles.successPopup}>{success}</div>}

        <FormInput
          label="Digite o código"
          icon={<FaLock />}
          type="text" // 'text' é melhor para códigos (pode ter zeros à esquerda)
          name="token"
          placeholder="Código de 6 dígitos"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          required={true}
          maxLength={6} // Limita a 6 dígitos
        />

        <Button type="submit" variant="primary" disabled={loading}>
          {loading ? 'A verificar...' : 'Confirmar'}
        </Button>
      </form>
    </div>
  );
};

export default PasswordVerifyCodePage;