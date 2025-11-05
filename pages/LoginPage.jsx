import React, { useState } from 'react'; // NOVO: importamos o 'useState'
import Button from '../components/Button.jsx';
import FormInput from '../components/FormInput.jsx';
import styles from './AuthForm.module.css';
import logoUebax from "../assets/logo.png";
import { FaUser, FaLock } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../utils/apiService.js';

// NOVO: Este é o endereço da sua "Fábrica" (o backend Django)
const API_URL = 'http://127.0.0.1:8000/api';

const LoginPage = () => {
  const navigate = useNavigate();
  // NOVO: Estado para guardar os dados do formulário
  const [formData, setFormData] = useState({
    email: '', // Nota: Mudei de 'username' para 'email' para bater com a API
    password: '',
  });

  // NOVO: Estado para guardar a mensagem de erro da API
  const [error, setError] = useState('');

  // NOVO: Função para atualizar o estado quando o usuário digita
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value,
    }));
  };

  // NOVO: A função principal que é chamada no "submit"
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
        // 2. CHAMA NOSSO NOVO "CARTEIRO"
        // Note 'skipAuth: true' (não precisamos de token para logar)
        // E não precisamos do URL completo, só do endpoint
        const data = await apiFetch('/login/', {
            method: 'POST',
            skipAuth: true, // Diz ao 'apiFetch' para NÃO enviar um token
            body: JSON.stringify(formData),
        });

        // SUCESSO!
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        navigate('/dashboard');

    } catch (err) {
        // FALHA! (Pega a mensagem de erro do 'apiFetch')
        console.error(err);
        if (err.message.includes('No active account')) {
            setError('Usuário ou senha incorretos.');
        } else {
            setError('Não foi possível conectar ao servidor.');
        }
    }
};

  return (
    <div className={styles.pageContainer}>
      
      <img src={logoUebax} alt="Logo UEBAX" className={styles.logo} />

      {/* NOVO: Conectamos o 'onSubmit' à nossa função */}
      <form className={styles.loginForm} onSubmit={handleSubmit}>

        {/* NOVO: Mostra o pop-up de erro se 'error' não estiver vazio */}
        {error && <div className={styles.errorPopup}>{error}</div>}

        <FormInput
          label="USUÁRIO"
          hint="(Apenas números)"
          icon={<FaUser />}
          type="text" // Seu design pedia "Apenas números", mude para type="number" se preferir
          name="email"  // Mudei para 'email'
          // NOVO: Conectamos o input ao nosso 'state'
          value={formData.email}
          onChange={handleChange}
        />
        
        <FormInput
          label="SENHA"
          icon={<FaLock />}
          type="password"
          name="password"
          // NOVO: Conectamos o input ao nosso 'state'
          value={formData.password}
          onChange={handleChange}
        />

        <Button 
          type="button" 
          variant="text"
          className={styles.forgotLink} // Reutiliza o estilo de alinhamento
          onClick={() => navigate('/redefinir-senha')} // <-- Navega ao clicar
        >
          Esqueci a senha
        </Button>

        <Button type="submit" variant="primary">
          ENTRAR
        </Button>

        <span className={styles.separator}>ou</span>

        <Button type="button" variant="text" onClick={() => navigate('/cadastro')}>
          Criar conta
        </Button>
      </form>
    </div>
  );
};

export default LoginPage;