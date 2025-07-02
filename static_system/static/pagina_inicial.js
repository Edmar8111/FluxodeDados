document.querySelector('#selectModalidade').addEventListener('change', function () {
      window.location.href = `http://${window.location.host}/page/${this.value}`;
    });

    document.querySelector('#tituloIndex').innerHTML = 
      window.location.pathname.includes('lucroPresumido') ? 'LUCRO PRESUMIDO' : 'SIMPLES NACIONAL';

    setTimeout(function () {
      const btSearch = document.querySelector('#bt-search');
      const kind = document.querySelector('#kind-search');
      const search = document.querySelector('#search');
      const main = document.querySelector('main');
      const arrayObjects = Array.from(document.querySelectorAll('div.card'));

      btSearch.addEventListener('click', function () {
        main.innerHTML = '';
        const value = search.value.toUpperCase();
        const valueCnpj=search.value.replace(/[.\-\/]/g, '')

        arrayObjects.forEach(card => {
          const cnpj = card.children[2].textContent.slice(2).trim();
          const nome = card.children[0].textContent.trim().toUpperCase();
          
          
          if ((kind.value === 'cnpj')) {
            searchRefined=''
            if(valueCnpj.length>2&&valueCnpj.length<=5){searchRefined=`${valueCnpj.slice(0, 2)}.${valueCnpj.slice(2)}`}
            if(valueCnpj.length>5&&valueCnpj.length<=8){searchRefined=`${valueCnpj.slice(0, 2)}.${valueCnpj.slice(2,5)}.${valueCnpj.slice(5)}`}
            if(valueCnpj.length>8&&valueCnpj.length<=12){searchRefined=`${valueCnpj.slice(0, 2)}.${valueCnpj.slice(2,5)}.${valueCnpj.slice(5,8)}/${valueCnpj.slice(8,12)}`}
            if(valueCnpj.length>12){searchRefined=`${valueCnpj.slice(0, 2)}.${valueCnpj.slice(2,5)}.${valueCnpj.slice(5,8)}/${valueCnpj.slice(8,12)}-${valueCnpj.slice(12,14)}`}
            if(searchRefined!=''&&cnpj.startsWith(searchRefined)){main.appendChild(card);}
            if(search.value.length<=2&&cnpj.slice(0,search.value.length)==search.value){main.appendChild(card)}
          }
          if ((kind.value === 'nome' && nome.startsWith(value))) {main.appendChild(card); };
        });
        if(main.innerHTML==''&&main.children[0]!='<h1 style="display:flex;justify-content:center;font-family:monospace;color:cadetblue;">Não Há Dados a Retornar!</h1>'){main.innerHTML='<h1 style="display:flex;justify-content:center;font-family:monospace;color:cadetblue;">Não Há Dados a Retornar!</h1>'}
      });
    }, 1000);