const chavesA = [
"A401","A402",
"A405","A406","A407","A408",
"A501",
"A504","A505","A506","A507"
];

const chavesB = [
"B101","B102","B106","B107",
"B201","B202",
"B206","B207","B208","B209","B210",
"B404","B405",
"B501","B503","B505","B509",
"B511","B513","B515","B516"
];

/* SIMULAÇÃO BANCO */
let emprestimos = {
    "A405":{
        funcionario:"Carlos Silva",
        id:"123",
        data:"10/04/2026 14:20:00"
    },
    "B209":{
        funcionario:"Ana Souza",
        id:"456",
        data:"10/04/2026 15:10:00"
    }
};

function agrupar(lista){
    const grupos = {};

    lista.forEach(codigo=>{
        const andar = codigo.substring(0,2)+"00";

        if(!grupos[andar]){
            grupos[andar] = [];
        }

        grupos[andar].push(codigo);
    });

    return grupos;
}

function render(lista,id){
    const container = document.getElementById(id);
    container.innerHTML = "";

    const grupos = agrupar(lista);

    Object.keys(grupos).sort().forEach(andar=>{

        const wrapper = document.createElement("div");
        wrapper.classList.add("linha-container");

        const titulo = document.createElement("div");
        titulo.classList.add("linha-titulo");
        titulo.innerText = andar;

        const linha = document.createElement("div");
        linha.classList.add("linha");

        grupos[andar].sort().forEach(nome=>{

            const div = document.createElement("div");
            div.classList.add("chave");
            div.innerText = nome;
            div.id = "key-" + nome;

            if(emprestimos[nome]){
                div.classList.add("retirada");
            }else{
                div.classList.add("disponivel");
            }

            div.addEventListener("click",()=>{
                if(emprestimos[nome]){
                    abrirModal(nome);
                }
            });

            linha.appendChild(div);
        });

        wrapper.appendChild(titulo);
        wrapper.appendChild(linha);
        container.appendChild(wrapper);

    });
}

function registrar(tipo){

    const id = document.getElementById("idFuncionario").value.trim();
    const chave = document.getElementById("codigoChave").value.trim().toUpperCase();

    if(!id || !chave) return;

    const el = document.getElementById("key-" + chave);
    if(!el) return;

    if(tipo === "RETIRADA"){

        if(emprestimos[chave]){
            abrirModal(chave);
            return;
        }

        emprestimos[chave] = {
            funcionario:"Funcionário " + id,
            id:id,
            data:new Date().toLocaleString()
        };

        el.classList.remove("disponivel");
        el.classList.add("retirada");
    }

    else{

        delete emprestimos[chave];

        el.classList.remove("retirada");
        el.classList.add("disponivel");
    }

    document.getElementById("idFuncionario").value = "";
    document.getElementById("codigoChave").value = "";
    document.getElementById("idFuncionario").focus();
}

function abrirModal(chave){

    const dados = emprestimos[chave];

    document.getElementById("modalConteudo").innerHTML = `
        <p><strong>Chave:</strong> ${chave}</p>
        <p><strong>Funcionário:</strong> ${dados.funcionario}</p>
        <p><strong>ID:</strong> ${dados.id}</p>
        <p><strong>Retirada em:</strong> ${dados.data}</p>
        <p><strong>Status:</strong> Emprestada</p>
    `;

    document.getElementById("modalOverlay").classList.remove("hidden");
}

function fecharModal(){
    document.getElementById("modalOverlay").classList.add("hidden");
}

render(chavesA,"blocoA");
render(chavesB,"blocoB");