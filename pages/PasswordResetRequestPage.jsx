import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/Button.jsx';
import FormInput from '../components/FormInput.jsx';
import styles from './AuthForm.module.css'; // <-- Reutilizando o CSS!
import logoUebax from "../assets/logo.png";
import { apiFetch } from '../utils/apiService.js';
import { FaEnvelope } from 'react-icons/fa'; // Ícone de Email

const PasswordResetRequestPage = () => {
  const navigate = useNavigate();
  
  // Estados para o email, erro e carregamento
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  // NOVO: Estado para mensagem de SUCESSO
  const [success, setSuccess] = useState('');

  // Lógica de Submissão
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      // 1. Chamar a API que fizemos (Tela 3 do backend)
      await apiFetch('/password-reset/request/', {
        method: 'POST',
        skipAuth: true, // Não precisa de token
        body: JSON.stringify({ email: email }),
      });
      
      // 2. SUCESSO!
      setLoading(false);
      
      // Em vez de um 'alert', mostramos uma mensagem de sucesso
      // e preparamos para redirecionar o usuário.
      setSuccess('Código enviado! A redirecionar...');

      // 3. Redirecionar para o Ecrã 2 (Verificação de Código)
      // (Como diz a sua especificação original)
      setTimeout(() => {
        // Passamos o email para o próximo ecrã, para sabermos quem está a verificar
        navigate('/verificar-codigo', { state: { email: email } });
      }, 2000); // Espera 2 segundos

    } catch (err) {
      // 4. ERRO! (A nossa API já devolve "E-mail Inválido")
      setLoading(false);
      setError(err.message || 'Falha ao enviar o pedido.');
      console.error(err);
    }
  };

  return (
    <div className={styles.pageContainer}>
      <img src={logoUebax} alt="Logo UEBAX" className={styles.logo} />

      {/* Títulos */}
      <h2 className={styles.authTitle}>Redefinir senha</h2>
      <p className={styles.authSubtitle}>Digite seu E-Mail no campo abaixo</p>

      <form className={styles.loginForm} onSubmit={handleSubmit}>
        
        {/* Pop-up de Erro (vermelho) */}
        {error && <div className={styles.errorPopup}>{error}</div>}
        
        {/* Pop-up de Sucesso (verde) */}
        {success && <div className={styles.successPopup}>{success}</div>}

        <FormInput
          // Desta vez não precisamos do 'label', como no design
          icon={<FaEnvelope />}
          type="email"
          name="email"
          placeholder="Seu e-mail"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required={true}
        />

        <Button type="submit" variant="primary" disabled={loading}>
          {loading ? 'A enviar...' : 'Confirmar'}
        </Button>
      </form>
    </div>
  );
};

export default PasswordResetRequestPage;