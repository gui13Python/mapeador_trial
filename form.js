document.addEventListener("DOMContentLoaded", function() {
  const form = document.getElementById("trial-form");
  const submitBtn = document.getElementById("submit-btn");

  // LISTA BRANCA: Só aceita provedores reais
  const allowedDomains = [
    "gmail.com", "hotmail.com", "outlook.com", "outlook.com.br",
    "yahoo.com", "yahoo.com.br", "icloud.com", "live.com", 
    "uol.com.br", "bol.com.br", "ig.com.br", "terra.com.br", 
    "proton.me", "protonmail.com"
  ];

  if (form) {
    form.addEventListener("submit", function(event) {
      event.preventDefault(); // Impede a página de atualizar
      
      const emailInput = document.getElementById('user-email').value.trim().toLowerCase();
      
      if (!emailInput.includes('@')) {
        alert("Por favor, insira um e-mail válido.");
        return;
      }

      const emailDomain = emailInput.split('@')[1];

      // Bloqueia e-mail se não estiver na lista permitida
      if (!allowedDomains.includes(emailDomain)) {
        alert("⚠️ Por razões de segurança, utilize um e-mail real (Gmail, Hotmail, Outlook, Yahoo, etc.) para liberar seu teste grátis.");
        return;
      }

      // Inicia o processo de envio
      submitBtn.innerText = "Enviando... Aguarde";
      submitBtn.disabled = true;

      const data = new FormData(event.target);

      // Envia via AJAX para o Formspree
      fetch(event.target.action, {
        method: form.method,
        body: data,
        headers: {
          'Accept': 'application/json'
        }
      }).then(response => {
        if (response.ok) {
          // SUCESSO: Abre o link do MEGA em uma nova aba imediatamente!
          window.open("https://mega.nz/file/SsZBVKbY#hsxP1u7SeeIc2BUQpXNFBAeUh_vu0z3Flhv44V80-sw", "_blank", "noopener,noreferrer");
          
          // Volta o botão ao normal e limpa o campo de e-mail caso ele queira clicar de novo
          submitBtn.innerText = "Liberar versão trial grátis";
          submitBtn.disabled = false;
          form.reset();
          
        } else {
          alert("Ocorreu um erro no servidor. Por favor, tente novamente.");
          submitBtn.innerText = "Liberar versão trial grátis";
          submitBtn.disabled = false;
        }
      }).catch(error => {
        alert("Erro de conexão. Verifique sua internet.");
        submitBtn.innerText = "Liberar versão trial grátis";
        submitBtn.disabled = false;
      });
    });
  }
});