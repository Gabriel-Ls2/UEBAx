import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/Button.jsx';
import FormInput from '../components/FormInput.jsx';
import styles from './AuthForm.module.css'; // <-- Reutilizando o CSS!
import logoUebax from "../assets/logo.png";
import { apiFetch } from '../utils/apiService.js';

// Ícones que precisamos
import { FaUser, FaLock, FaEnvelope, FaIdCard } from 'react-icons/fa';

const CadastroPage = () => {
  const navigate = useNavigate();
  
  // Estados para todos os campos do formulário
  const [formData, setFormData] = useState({
    nome_completo: '',
    cpf: '',
    email: '',
    password: '',
    password2: '', // Para a "Confirmação de Senha"
  });
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Um 'handler' genérico para atualizar todos os campos
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // Lógica de Submissão
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // 1. Validação "Front-end" (como você especificou)
    if (formData.password !== formData.password2) {
      setError('As senhas não coincidem');
      setLoading(false);
      return;
    }

    // 2. Tentar enviar para a API
    try {
      // O 'apiFetch' é o nosso "Carteiro"
      await apiFetch('/register/', {
        method: 'POST',
        skipAuth: true, // Não precisa de token para se registar
        body: JSON.stringify(formData),
      });
      
      // 3. Sucesso!
      setLoading(false);
      alert('Cadastro realizado com sucesso!');
      navigate('/login'); // Envia o usuário para o login

    } catch (err) {
      // 4. Erro!
      setLoading(false);
      // 'err.message' vem da nossa API (ex: "Este email já existe")
      setError(err.message);
      console.error(err);
    }
  };

  return (
    <div className={styles.pageContainer}>
      <img src={logoUebax} alt="Logo UEBAX" className={styles.logo} />

      {/* O Título "Cadastro" (novo no design) */}
      <div className={styles.pageTitleBar}>Cadastro</div>

      <form className={styles.loginForm} onSubmit={handleSubmit}>
        
        {/* Pop-up de Erro */}
        {error && <div className={styles.errorPopup}>{error}</div>}

        <FormInput
          label="Nome Completo"
          icon={<FaUser />}
          type="text"
          name="nome_completo"
          value={formData.nome_completo}
          onChange={handleChange}
          required={true} // <-- O nosso asterisco a funcionar!
        />
        <FormInput
          label="CPF"
          icon={<FaIdCard />} // Ícone de CPF
          type="text" // Usar 'text' é melhor para máscaras de CPF
          name="cpf"
          value={formData.cpf}
          onChange={handleChange}
          required={true}
        />
        <FormInput
          label="E-Mail"
          icon={<FaEnvelope />} // Ícone de Email
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required={true}
        />
        <FormInput
          label="Senha"
          icon={<FaLock />}
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          required={true}
        />
        <FormInput
          label="Confirme sua senha"
          icon={<FaLock />}
          type="password"
          name="password2"
          value={formData.password2}
          onChange={handleChange}
          required={true}
        />

        <Button type="submit" variant="primary" disabled={loading}>
          {/* Mostra "Aguarde..." enquanto a API responde */}
          {loading ? 'Aguarde...' : 'Cadastrar'}
        </Button>

        <span className={styles.separator}>ou</span>

        <Button 
          type="button" 
          variant="text"
          onClick={() => navigate('/login')} // <-- Faz ele navegar para o login
        >
          Já tem uma conta? Fazer login
        </Button>
      </form>
    </div>
  );
};

export default CadastroPage;