import React from 'react';
import styles from './LatestAlertsList.module.css';
import { FaExclamationTriangle } from 'react-icons/fa'; // O nosso ícone de alerta

/**
 * A lista de "Últimos alertas" para o card da direita.
 * Recebe a lista de 'alerts' vinda da API.
 */
const LatestAlertsList = ({ alerts = [] }) => {
  return (
    <div className={styles.listContainer}>
      {alerts.length === 0 ? (
        <p className={styles.emptyText}>Nenhum alerta recente.</p>
      ) : (
        <ul className={styles.list}>
          {/* Fazemos um loop pelos alertas e criamos um <li> para cada */}
          {alerts.map((alert, index) => (
            <li key={index} className={styles.listItem}>
              <div className={styles.iconWrapper}>
                <FaExclamationTriangle />
              </div>
              {/* O 'alert.descricao' vem da nossa API (ex: "Acesso fora do horário") */}
              <span className={styles.description}>{alert.descricao}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default LatestAlertsList;