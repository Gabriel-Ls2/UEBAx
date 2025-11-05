import React from 'react';
import styles from './Button.module.css';

/**
 * Botão reutilizável.
 * @param {('primary' | 'text')} variant - O estilo do botão.
 */
const Button = ({ children, variant = 'primary', ...props }) => {
  // Isso aplica a classe base 'button' e a classe da variante (ex: 'primary')
  const buttonClassName = `${styles.button} ${styles[variant]}`;

  return (
    <button className={buttonClassName} {...props}>
      {children}
    </button>
  );
};

export default Button;