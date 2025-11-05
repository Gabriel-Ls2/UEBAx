import React from 'react';
import styles from './FormInput.module.css';

/**
 * Input de formulário customizado com ícone, label e hint.
 */
const FormInput = ({ label, hint, icon, required = false, ...inputProps }) => {
  return (
    <div className={styles.inputWrapper}>
      {/* Container para o Label e o Hint */}
      <div className={styles.labelContainer}>
        <label className={styles.label}>
          {label}
          {/* NOVO: Se 'required' for 'true', mostramos o asterisco */}
          {required && <span className={styles.requiredStar}> *</span>}
        </label>
        {hint && <span className={styles.hint}>{hint}</span>}
      </div>
      
      {/* Container para o Ícone e o Input */}
      <div className={styles.inputContainer}>
        {icon && <span className={styles.icon}>{icon}</span>}
        <input className={styles.input} {...inputProps} />
      </div>
    </div>
  );
};

export default FormInput;