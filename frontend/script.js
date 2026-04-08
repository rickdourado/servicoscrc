document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://localhost:8000/api';
    
    // UI Elements
    const poolSgrc = document.getElementById('pool-sgrc');
    const poolPrefrio = document.getElementById('pool-prefrio');
    const dropzone = document.getElementById('dropzone');
    const structureContent = document.getElementById('structure-content');
    const saveBtn = document.getElementById('save-btn');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const viewSections = document.querySelectorAll('.view-section');

    let itemsData = [];

    // Initialize API Call
    fetchData();

    // Tab Switching Logic
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            viewSections.forEach(s => s.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(btn.dataset.target).classList.add('active');
            
            if(btn.dataset.target === 'view-structure') {
                updateStructureView();
            }
        });
    });

    // Save Button Logic
    saveBtn.addEventListener('click', async () => {
        saveBtn.textContent = "Salvando...";
        saveBtn.disabled = true;

        const orderedIds = Array.from(dropzone.children).map(bubble => bubble.dataset.id);
        const orderedItemsData = orderedIds.map(id => itemsData.find(item => item.id === id)).filter(Boolean);

        try {
            const res = await fetch(`${API_URL}/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ items: orderedItemsData })
            });
            const data = await res.json();
            alert(`Sucesso! ${data.message} em ${data.path}`);
        } catch(e) {
            console.error("Save error:", e);
            alert("Erro ao salvar.");
        } finally {
            saveBtn.textContent = "Salvar Estrutura";
            saveBtn.disabled = false;
        }
    });

    async function fetchData() {
        try {
            const res = await fetch(`${API_URL}/data`);
            const data = await res.json();
            itemsData = data.items;
            renderBubbles(itemsData);
        } catch(e) {
            console.error(e);
            poolSgrc.innerHTML = '<p style="color:red">Erro ao carregar dados do Backend. (Servidor rodando?)</p>';
        }
    }

    function renderBubbles(items) {
        poolSgrc.innerHTML = '';
        poolPrefrio.innerHTML = '';
        dropzone.innerHTML = '';
        
        items.forEach(item => {
            const bubble = document.createElement('div');
            bubble.classList.add('bubble');
            
            // Designação de classe e data
            bubble.dataset.id = item.id;
            bubble.dataset.source = item.source; // 'SGRC' ou 'Prefrio'
            
            if (item.source === 'SGRC') {
                bubble.classList.add('sgrc');
            } else {
                bubble.classList.add('prefrio');
            }
            
            // Texto (+ Icone opcional de acao)
            bubble.innerHTML = `<span>${item.name}</span>`;

            // Logica de click-to-add / click-to-remove
            bubble.addEventListener('click', () => {
                if (bubble.parentElement === dropzone) {
                    // Remover da dropzone (Volta pra sua pool original)
                    if (bubble.dataset.source === 'SGRC') {
                        poolSgrc.appendChild(bubble);
                    } else {
                        poolPrefrio.appendChild(bubble);
                    }
                } else {
                    // Adicionar na dropzone
                    dropzone.appendChild(bubble);
                }
                updateStructureView();
            });

            // Append Inicial
            if (item.source === 'SGRC') {
                poolSgrc.appendChild(bubble);
            } else {
                poolPrefrio.appendChild(bubble);
            }
        });
    }

    // Tab 2 Generation
    function updateStructureView() {
        const orderedIds = Array.from(dropzone.children).map(b => b.dataset.id);
        
        if (orderedIds.length === 0) {
            structureContent.innerHTML = '<p style="color:var(--text-secondary)">Nenhuma área selecionada na estrutura principal ainda.</p>';
            return;
        }

        let html = '';
        orderedIds.forEach(id => {
            const item = itemsData.find(i => i.id === id);
            if(item) {
                const sourceClass = item.source === 'SGRC' ? 'sgrc' : 'prefrio';
                
                html += `<div class="view-item ${sourceClass}">
                    <h3>
                        <span class="source-badge">${item.source}</span>
                        ${item.name}
                    </h3>
                    <ul>`;
                
                if (item.level2 && item.level2.length > 0) {
                    item.level2.forEach(n2 => {
                        html += `<li>${n2}</li>`;
                    });
                } else {
                    html += `<li><em style="opacity:0.5">Sem serviços associados</em></li>`;
                }
                
                html += `</ul></div>`;
            }
        });

        structureContent.innerHTML = html;
    }
});
