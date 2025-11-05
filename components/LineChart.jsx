import React from 'react';
// 1. Importar as ferramentas da Chart.js
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler, // Importante para a área sombreada
} from 'chart.js';

// 2. Registar os "plugins" que vamos usar (isto é obrigatório)
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

/**
 * O nosso componente de Gráfico de Linha.
 * Recebe os 'labels' (ex: [0, 1, ... 23]) e os 'data' (ex: [0, 0, 2, 5, ...])
 * vindos da nossa API.
 */
const LineChart = ({ labels, data: chartData }) => {
  
  // 3. Configurar os DADOS do gráfico (o que vai ser desenhado)
  const data = {
    labels: labels.map(label => `${label} H`), // Transforma [9, 10] em ["9 H", "10 H"]
    datasets: [
      {
        label: 'Logins', // Legenda (não aparece no seu design, mas é bom ter)
        data: chartData, // Os dados [0, 0, 2, 5, ...]
        
        // --- Estilo da Linha (o seu design roxo) ---
        borderColor: '#5c4a8f', // A cor roxa escura da linha
        borderWidth: 3,
        
        // --- Estilo da Área Sombreada (o gradiente) ---
        fill: true, // Diz para preencher a área abaixo
        backgroundColor: (context) => {
          // Lógica do gradiente (para o efeito "fade")
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 200);
          gradient.addColorStop(0, 'rgba(216, 168, 216, 0.6)'); // Roxo claro (do seu botão)
          gradient.addColorStop(1, 'rgba(216, 168, 216, 0)');
          return gradient;
        },
        
        // --- Estilo dos Pontos ---
        pointBackgroundColor: '#5c4a8f',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        
        tension: 0.4, // Isto cria a curva suave (Bezier)
      },
    ],
  };

  // 4. Configurar as OPÇÕES do gráfico (o aspeto geral)
  const options = {
    responsive: true, // Faz o gráfico adaptar-se ao tamanho do container
    maintainAspectRatio: false, // Permite-nos controlar a altura
    scales: {
      y: {
        beginAtZero: true, // Eixo Y começa no 0
        grid: {
          drawBorder: false, // Remove a borda da grelha
        },
      },
      x: {
        grid: {
          display: false, // Remove as linhas verticais da grelha
        },
      },
    },
    plugins: {
      legend: {
        display: false, // Esconde a legenda "Logins" (como no seu design)
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: '#333',
      },
    },
    interaction: {
      intersect: false,
      mode: 'index',
    },
  };

  // 5. Renderizar o componente <Line>
 return (
    // NOVO: Adicionamos um 'wrapper' div
    // Isto dá ao Chart.js um 'container' com limites claros.
    // 'position: relative' é a chave para o 'responsive: true' funcionar.
    // '350px' é uma boa altura, pode ajustar se quiser.
    <div style={{ position: 'relative', height: '350px' }}>
      <Line options={options} data={data} />
    </div>
  );
};

export default LineChart;