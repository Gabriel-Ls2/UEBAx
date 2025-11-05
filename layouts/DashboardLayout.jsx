import React from 'react';
import SideMenu from '../components/SideMenu';
import styles from './DashboardLayout.module.css';
import { Outlet } from 'react-router-dom';

/**
 * Este componente cria o "molde" da página:
 * Menu Lateral fixo + Conteúdo principal à direita
 */
const DashboardLayout = () => {
  return (
    <div className={styles.layout}>
      <SideMenu />
      <main className={styles.content}>
        <Outlet />
      </main>
    </div>
  );
};

export default DashboardLayout;