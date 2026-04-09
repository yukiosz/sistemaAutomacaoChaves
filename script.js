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
        const grupos=agrupar(lista)
    
        Object.keys(grupos).sort().forEach(a=>{
            const wrapper=document.createElement("div")
            wrapper.classList.add("linha-container")
    
            const titulo=document.createElement("div")
            titulo.classList.add("linha-titulo")
            titulo.innerText=a
    
            const linha=document.createElement("div")
            linha.classList.add("linha")
    
            grupos[a].sort().forEach(nome=>{
                const div=document.createElement("div")
                div.classList.add("chave","disponivel")
                div.innerText=nome
                div.id="key-"+nome
                linha.appendChild(div)
            })
    
            wrapper.appendChild(titulo)
            wrapper.appendChild(linha)
            container.appendChild(wrapper)
        })
    }
    
    render(chavesA,"blocoA")
    render(chavesB,"blocoB")
    
    function registrar(tipo){
        const id=document.getElementById("idFuncionario").value
        const chave=document.getElementById("codigoChave").value
        const hora=new Date().toLocaleTimeString()
    
        if(!id || !chave) return
    
        const el=document.getElementById("key-"+chave)
    
        if(el){
            if(tipo==="RETIRADA"){
                el.classList.remove("disponivel")
                el.classList.add("retirada")
            }else{
                el.classList.remove("retirada")
                el.classList.add("disponivel")
            }
        }
    
        const log=document.getElementById("log")
        const linha=document.createElement("div")
        linha.innerText=`${hora} | ${tipo} | ${chave} | ID ${id}`
        log.prepend(linha)
    
        document.getElementById("codigoChave").value=""
        document.getElementById("idFuncionario").value=""
        document.getElementById("idFuncionario").focus()
    }