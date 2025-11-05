import React, { useState, useEffect } from 'react';
import { apiFetch } from '../utils/apiService.js';
import DataTable from '../components/DataTable.jsx'; // Reutilizando o mesmo componente!

const AlertasPage = () => {
  // MUDANÇA 1: Mudámos o nome do state
  const [alertas, setAlertas] = useState([]); 
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAlertas = async () => {
      try {
        setLoading(true);
        setError(''); // Limpa erros antigos
        
        // MUDANÇA 1: Corrigido para /alerts/ (sem o /api/)
        const data = await apiFetch('/alerts/'); 
        
        // MUDANÇA 2: Corrigido para data.results (como no Dashboard)
        setAlertas(data || []); 
        
      } catch (err) {
        console.error("Erro ao buscar alertas:", err);
        setError('Falha ao carregar os alertas.');
      } finally {
        setLoading(false);
      }
    };

    fetchAlertas();
  }, []);

  if (loading) return <div>A carregar alertas...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  // MUDANÇA 3: As novas colunas da tabela (do seu design)
  const headers = ['Descrição', 'Usuário', 'Data', 'Horário'];
  
  // MUDANÇA 4: As chaves do JSON do seu 'AlertaSerializer'
  // (Nós criámo-las no backend exatamente assim)
  const dataKeys = ['descricao', 'usuario_email', 'data', 'horario'];

  return (
    <div style={{ width: '100%' }}>
      {/* MUDANÇA 5: O título da página */}
      <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '30px' }}>
        ALERTAS
      </h1>
      
      <DataTable
        headers={headers}
        data={alertas}
        dataKeys={dataKeys}
      />
    </div>
  );
};

export default AlertasPage;