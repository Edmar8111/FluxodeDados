// Seleciona o container principal
  const container = document.getElementById('container');

  // Muda para o modo de registro
  function mudarParaRegistro() {
    container.classList.remove('login-mode');
    container.classList.add('register-mode');
  }

  // Muda para o modo de login
  function mudarParaLogin() {
    container.classList.remove('register-mode');
    container.classList.add('login-mode');
  }

  // Exemplo de interceptação dos formulários
  document.getElementById('form-login').onsubmit = function (e) {
    e.preventDefault();
    alert('Login efetuado!');
  };

  document.getElementById('form-registro').onsubmit = function (e) {
    e.preventDefault();
    alert('Registro realizado!');
  };