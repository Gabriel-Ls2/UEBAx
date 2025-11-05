import React from 'react';
import styles from './ConnectionStatusTable.module.css';

/**
 * A tabela "Status de conexão" para o dashboard.
 * Recebe a 'tabela_status_conexao' vinda da API.
 */
const ConnectionStatusTable = ({ statusData = [] }) => {
  return (
    <div className={styles.tableWrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Usuário</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {statusData.length === 0 ? (
            <tr>
              <td colSpan="2" className={styles.emptyText}>
                Nenhum usuário encontrado.
              </td>
            </tr>
          ) : (
            // Fazemos um loop pelos dados e criamos uma <tr> para cada
            statusData.map((user, index) => (
              <tr key={index}>
                {/* 'user.nome_usuario' vindo da API */}
                <td>{user.nome_usuario}</td>
                <td>
                  {/* Criamos o estilo "Ativo" vs "Inativo" */}
                  <span className={`${styles.status} ${
                      user.status === 'Ativo' ? styles.ativo : styles.inativo
                    }`}
                  >
                    {user.status}
                  </span>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default ConnectionStatusTable;