import React, { useState, useEffect } from 'react';
import { apiFetch } from '../utils/apiService.js';
import DataTable from '../components/DataTable.jsx'; // O nosso novo componente!

const EventosPage = () => {
  const [eventos, setEventos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchEventos = async () => {
      try {
        setLoading(true);
        // O seu endpoint de API que já está pronto!
        const data = await apiFetch('/events/'); 
        
        // A API devolve os dados em 'results'.
        // O seu serializer já formata os dados perfeitamente.
        setEventos(data || []); 
        
      } catch (err) {
        console.error("Erro ao buscar eventos:", err);
        setError('Falha ao carregar os eventos.');
      } finally {
        setLoading(false);
      }
    };

    fetchEventos();
  }, []);

  if (loading) return <div>A carregar eventos...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  // 1. Define os cabeçalhos (como no design)
  const headers = ['Usuário', 'Evento', 'Horário'];
  
  // 2. Define as chaves do JSON (do seu 'EventoSerializer')
  const dataKeys = ['usuario_email', 'evento_desc', 'horario'];

  return (
    <div style={{ width: '100%' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '30px' }}>
        EVENTOS
      </h1>
      
      {/* 3. Renderiza a tabela! */}
      <DataTable
        headers={headers}
        data={eventos}
        dataKeys={dataKeys}
      />
    </div>
  );
};

export default EventosPage;