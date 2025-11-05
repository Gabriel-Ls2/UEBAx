import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import styles from './SideMenu.module.css';
import logoUebax from '../assets/logo.png'; 


// Importando os ícones que precisamos
import { 
  FaHome,                 // Ícone de "casa" para Dashboard
  FaClock,                // Ícone de "relógio" para Eventos
  FaExclamationTriangle,  // Ícone de "alerta" para Alertas
  FaSignOutAlt            // Ícone de "sair"
} from "react-icons/fa";

// O 'apiService' que criamos antes para o Login.
// Vamos precisar dele para o Logout.
// Se você não o criou, aqui está a lógica de fetch:

import { apiFetch } from '../utils/apiService.js';

const SideMenu = () => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    const refreshToken = localStorage.getItem('refreshToken');

    try {
      // 2. CHAMA NOSSO NOVO "CARTEIRO"
      await apiFetch('/logout/', {
        method: 'POST',
        body: JSON.stringify({ refresh: refreshToken }),
        // Não precisamos de 'skipAuth', ele vai pegar o token por padrão
      });

    } catch (error) {
      console.error("Falha ao fazer logout no backend:", error);
    } finally {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      navigate('/login');
    }
  };

  return (
    <nav className={styles.menu}>
      <div className={styles.logoContainer}>
        <img src={logoUebax} alt="UEBAX Logo" className={styles.logo} />
        <span className={styles.logoText}>UEBAX</span>
      </div>

      <ul className={styles.navList}>
        {/* O NavLink sabe se está "ativo" e aplica o estilo */}
        <li>
          <NavLink 
            to="/dashboard" // Rota "índice"
            end // 'end' garante que ele só fica ativo em /dashboard exato
            className={({ isActive }) => 
              `${styles.navItem} ${isActive ? styles.active : ''}`
            }
          >
            <FaHome />
            <span>Dashboard</span>
          </NavLink>
        </li>
        <li>
          <NavLink 
            to="/dashboard/eventos" // A nossa nova rota!
            className={({ isActive }) => 
              `${styles.navItem} ${isActive ? styles.active : ''}`
            }
          >
            <FaClock />
            <span>Eventos</span>
          </NavLink>
        </li>
        <li>
          <NavLink 
            to="/dashboard/alertas" // TODO: A rota de alertas
            className={({ isActive }) => 
              `${styles.navItem} ${isActive ? styles.active : ''}`
            }
          >
            <FaExclamationTriangle />
            <span>Alertas</span>
          </NavLink>
        </li>
      </ul>

      <div className={styles.footer}>
        <button onClick={handleLogout} className={styles.logoutButton}>
          <FaSignOutAlt /> {/* <-- CORRIGIDO */}
          <span>Sair</span>
        </button>
      </div>
    </nav>
  );
};

export default SideMenu;