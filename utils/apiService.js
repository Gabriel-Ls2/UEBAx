const API_URL = 'http://127.0.0.1:8000/api';

/**
 * Pega o token de acesso armazenado no navegador.
 */
const getAuthToken = () => {
    return localStorage.getItem('accessToken');
};

/**
 * Função principal para TODAS as requisições autenticadas.
 * Ela automaticamente adiciona o "Bearer Token" no cabeçalho.
 */
export const apiFetch = async (endpoint, options = {}) => {
    const token = getAuthToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };
    if (token && !options.skipAuth) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers,
        });

        // Tenta sempre ler a resposta, mesmo se for um erro
        const data = response.status === 204 ? null : await response.json();

        if (!response.ok) {
            // --- LÓGICA DE ERRO MELHORADA ---
            let errorMessage = 'Ocorreu um erro na API'; // Fallback

            if (data) {
                // Tenta encontrar a primeira chave de erro (ex: "email", "cpf", "password")
                const firstErrorKey = Object.keys(data)[0]; 
                
                if (firstErrorKey && Array.isArray(data[firstErrorKey])) {
                    // Pega a primeira mensagem de erro. Ex: "Este email já está em uso."
                    errorMessage = data[firstErrorKey][0]; 
                } else if (data.detail) {
                    // Erros genéricos do DRF (ex: "Token inválido")
                    errorMessage = data.detail;
                }
            }
            // Lança o erro específico!
            throw new Error(errorMessage);
            // --- FIM DA LÓGICA MELHORADA ---
        }
        
        return data; // Sucesso

    } catch (err) {
        // Erro de rede (CORS, backend desligado) ou o erro que lançámos
        throw err;
    }
};