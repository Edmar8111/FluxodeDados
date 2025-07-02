// Função para redirecionar de forma simples
    function irPara(destino) {
      if (destino === 'login') {
        window.location.href = `/login`; // ajuste se necessário
      } else if (destino === 'cadastro') {
        window.location.href = `/register`;
      }
    }