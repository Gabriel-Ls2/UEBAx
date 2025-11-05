import React from 'react';
import styles from './StatCard.module.css';

/**
 * O componente para os 4 cards de estatística no topo.
 * Recebe um 'título' (ex: "Logins hoje") e um 'valor' (ex: "100").
 */
const StatCard = ({ title, value }) => {
  return (
    <div className={styles.card}>
      {/* O valor (o número grande) */}
      <span className={styles.value}>{value}</span>
      
      {/* O título (o texto pequeno) */}
      <span className={styles.title}>{title}</span>
    </div>
  );
};

export default StatCard;