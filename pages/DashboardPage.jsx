import React, { useState, useEffect } from 'react';
import { apiFetch } from '../utils/apiService.js';
import styles from './DashboardPage.module.css';
import StatCard from '../components/StatCard.jsx';
import LineChart from '../components/LineChart.jsx';
import ConnectionStatusTable from '../components/ConnectionStatusTable.jsx';
import LatestAlertsList from '../components/LatestAlertsList.jsx';

const DashboardPage = () => {
  // 2. Os seus 'states' (estão perfeitos, não mexa)
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // 3. O seu 'useEffect' (está perfeito, não mexa)
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError('');

        const [statsData, alertsData] = await Promise.all([
          apiFetch('/dashboard/stats/'),
          // Nota: O seu design mostra 3 alertas, vamos pedir 3
          apiFetch('/alerts/?limit=3') 
        ]);
        
        setStats(statsData);
        setAlerts(alertsData.results); // O DRF coloca os resultados em 'results'

      } catch (err) {
        console.error("Erro ao buscar dados do dashboard:", err);
        setError('Falha ao carregar os dados. Tente fazer login novamente.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  
  // 4. A sua lógica de 'loading' e 'error' (perfeita)
  if (loading) {
    return <div style={{padding: '20px'}}>A carregar dados do dashboard...</div>;
  }
  if (error) {
    return <div style={{ color: 'red', padding: '20px' }}>{error}</div>;
  }

  // 5. O NOVO RENDER (Onde a magia acontece)
  return (
    <div className={styles.pageWrapper}>
      
      {/* --- Secção dos 4 Cards de Estatística --- */}
      <div className={styles.statsGrid}>
        {/* Usamos o 'stats' que veio da API para alimentar os cards */}
        <StatCard 
          title="Logins hoje" 
          value={stats?.cards?.logins_hoje} 
        />
        <StatCard 
          title="Alertas ativos" 
          value={stats?.cards?.alertas_ativos} 
        />
        <StatCard 
          title="Dispositivos conectados" 
          value={stats?.cards?.dispositivos_conectados} 
        />
        <StatCard 
          title="Último evento" 
          value={stats?.cards?.ultimo_evento} 
        />
      </div>

      {/* --- Secção do Gráfico --- */}
      <div className={styles.chartContainer}>
        <h3 className={styles.sectionTitle}>Logins por hora</h3>

        {/* Alimentamo-lo com os dados do 'stats' */}
        {stats?.grafico_logins_por_hora && (
            <LineChart 
            labels={stats.grafico_logins_por_hora.labels}
            data={stats.grafico_logins_por_hora.data}
            />
        )}

      </div>

      {/* --- Secção da Tabela de Status --- */}
      <div className={styles.tableContainer}>
        <h3 className={styles.sectionTitle}>Status de conexão</h3>

        {/* 2. O NOSSO NOVO COMPONENTE DE TABELA */}
        <ConnectionStatusTable 
            statusData={stats?.tabela_status_conexao} 
        />

      </div>

      {/* --- Secção dos Últimos Alertas --- */}
      <div className={styles.alertsContainer}>
        <h3 className={styles.sectionTitle}>Últimos alertas</h3>

        {/* 3. O NOSSO NOVO COMPONENTE DE LISTA */}
        <LatestAlertsList alerts={alerts} />

      </div>

    </div>
  );
};

export default DashboardPage;