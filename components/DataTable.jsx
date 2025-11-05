import React from 'react';
import styles from './DataTable.module.css';

/**
 * Componente de tabela reutilizável para os relatórios.
 * @param {string[]} headers - Um array de strings para os cabeçalhos (ex: ['Usuário', 'Evento'])
 * @param {object[]} data - Um array de objetos com os dados
 * @param {string[]} dataKeys - As chaves para extrair os dados (ex: ['usuario_email', 'evento_desc'])
 */
const DataTable = ({ headers = [], data = [], dataKeys = [] }) => {
  return (
    <div className={styles.tableContainer}>
      <table className={styles.table}>
        <thead>
          <tr>
            {headers.map((header) => (
              <th key={header}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={headers.length} className={styles.emptyText}>
                Nenhum dado encontrado.
              </td>
            </tr>
          ) : (
            data.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {/* Faz um loop pelas 'dataKeys' para construir cada célula */}
                {dataKeys.map((key) => (
                  <td key={`${rowIndex}-${key}`}>{row[key]}</td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;