let emprestimos = []

const chavesA = [
"A401","A402","A405","A406","A407","A408",
"A501","A504","A505","A506","A507"
];

const chavesB = [
"B101","B102","B106","B107",
"B201","B202","B206","B207","B208","B209","B210",
"B404","B405",
"B501","B503","B505","B509",
"B511","B513","B515","B516"
];

async function carregarEstado(){
    const r = await fetch("/estado")
    emprestimos = await r.json()

    render(chavesA,"blocoA")
    render(chavesB,"blocoB")
}

function agrupar(lista){
    const grupos={}
    lista.forEach(c=>{
        const andar=c.substring(0,2)+"00"
        if(!grupos[andar]) grupos[andar]=[]
        grupos[andar].push(c)
    })
    return grupos
}

function render(lista,id){
    const container=document.getElementById(id)
    container.innerHTML=""

    const grupos=agrupar(lista)

    Object.keys(grupos).sort().forEach(andar=>{

        const wrapper=document.createElement("div")
        wrapper.classList.add("linha-container")

        const titulo=document.createElement("div")
        titulo.classList.add("linha-titulo")
        titulo.innerText=andar

        const linha=document.createElement("div")
        linha.classList.add("linha")

        grupos[andar].sort().forEach(nome=>{

            const div=document.createElement("div")
            div.classList.add("chave")
            div.innerText=nome
            div.id="key-"+nome

            if(emprestimos.includes(nome)){
                div.classList.add("retirada")
            }else{
                div.classList.add("disponivel")
            }

            div.addEventListener("click",()=>abrirModal(nome))

            linha.appendChild(div)
        })

        wrapper.appendChild(titulo)
        wrapper.appendChild(linha)
        container.appendChild(wrapper)
    })
}

async function registrar(tipo){

    const id=document.getElementById("idFuncionario").value.trim()
    const chave=document.getElementById("codigoChave").value.trim().toUpperCase()

    if(!id || !chave) return

    await fetch("/registrar",{
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body:JSON.stringify({
            id:id,
            chave:chave,
            tipo:tipo
        })
    })

    document.getElementById("idFuncionario").value=""
    document.getElementById("codigoChave").value=""
    document.getElementById("idFuncionario").focus()

    carregarEstado()
}

async function abrirModal(chave){

    const r = await fetch("/info/"+chave)
    const dados = await r.json()

    if(!dados.chave) return

    document.getElementById("modalConteudo").innerHTML=`
        <p><strong>Chave:</strong> ${dados.chave}</p>
        <p><strong>Funcionário:</strong> ${dados.nome}</p>
        <p><strong>ID:</strong> ${dados.id}</p>
        <p><strong>Retirada em:</strong> ${dados.data}</p>
        <p><strong>Status:</strong> Emprestada</p>
    `

    document.getElementById("modalOverlay").classList.remove("hidden")
}

function fecharModal(){
    document.getElementById("modalOverlay").classList.add("hidden")
}

carregarEstado()
