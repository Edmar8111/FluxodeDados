async function cnae_request(cnae, tag) {
            try {
                const response = await fetch(`http://${window.location.host}/cnae/${cnae}`, { method: 'POST' });
                const data = await response.json();
                const info = Array.isArray(data) ? data[0] : data;

                document.getElementById("cnae-id").innerText = info.id;
                document.getElementById("atividade-principal").innerText = info.descricao;
                document.getElementById("grupo").innerText = info.classe.grupo.descricao;
                document.getElementById("divisao").innerText = info.classe.grupo.divisao.descricao;
                document.getElementById("secao").innerText = info.classe.grupo.divisao.secao.descricao;
                document.getElementById("observacoes").innerText = info.observacoes;
                document.getElementById("descricao").innerText = info.descricao;
                document.getElementById("referencia").innerText = `ID de Referência: ${info.id} CNAE`;

                document.getElementById("fiscal-anexo").innerText = info.anexo_info?.anexo || 'N/A';
                document.getElementById("fiscal-fator").innerText = info.anexo_info.fator_r==true ? 'Sim' : 'Não';
                document.getElementById("fiscal-aliquota").innerText = `${parseFloat(info.anexo_info?.aliquota_inicial)}%` || 'N/A';

                const secAtividades = document.getElementById("atividade-secundaria");
                secAtividades.innerHTML = "";
                info.atividades?.forEach(atividade => {
                    const p = document.createElement('p');
                    p.innerText = atividade;
                    secAtividades.appendChild(p);
                });

                tag.style.display = "block";
                tag.scrollIntoView({ behavior: 'smooth' });
            } catch (erro) {
                alert("Erro ao buscar os dados. Verifique o código informado.");
            }
        }

        function consultar() {
            const input = document.getElementById("inputConsulta").value.trim();
            const resultado = document.getElementById("resultado");
            if (input !== "") {
                cnae_request(input, resultado);
            } else {
                alert("Digite um código válido para consultar.");
            }
        }