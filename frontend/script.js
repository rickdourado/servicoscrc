document.addEventListener('DOMContentLoaded', () => {
    const isLocalDev = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && window.location.port === '3000';
    const API_URL = isLocalDev ? 'http://localhost:8000/api' : '/api';
    
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
                    <ul class="dnd-list" data-parent-id="${item.id}" style="min-height: 40px; border-radius: 4px; transition: all 0.2sease;">`;
                
                if (item.level2 && item.level2.length > 0) {
                    item.level2.forEach((n2, idx) => {
                        html += `<li draggable="true" style="cursor: grab;" data-parent-id="${item.id}" data-item-idx="${idx}" title="Arraste para outra estrutura">${n2}</li>`;
                    });
                } else {
                    html += `<li class="empty-placeholder"><em style="opacity:0.5">Vazio (Arraste itens para cá)</em></li>`;
                }
                
                html += `</ul></div>`;
            }
        });

        structureContent.innerHTML = html;
        attachDragAndDropHandlers();
    }

    let draggedInfo = null;

    function attachDragAndDropHandlers() {
        const lists = structureContent.querySelectorAll('.dnd-list');
        const items = structureContent.querySelectorAll('li[draggable="true"]');

        items.forEach(item => {
            item.addEventListener('dragstart', (e) => {
                draggedInfo = {
                    parentId: item.dataset.parentId,
                    itemIdx: parseInt(item.dataset.itemIdx, 10)
                };
                item.style.opacity = '0.4';
                item.style.boxShadow = '0 0 10px rgba(0, 74, 128, 0.4)';
            });
            item.addEventListener('dragend', () => {
                item.style.opacity = '1';
                item.style.boxShadow = 'none';
                draggedInfo = null;
            });
        });

        lists.forEach(list => {
            list.addEventListener('dragover', (e) => {
                e.preventDefault(); 
                list.style.background = 'rgba(0, 74, 128, 0.05)';
                list.style.boxShadow = 'inset 0 0 0 2px rgba(0, 74, 128, 0.3)';
            });
            list.addEventListener('dragleave', () => {
                list.style.background = '';
                list.style.boxShadow = '';
            });
            list.addEventListener('drop', (e) => {
                e.preventDefault();
                list.style.background = '';
                list.style.boxShadow = '';
                const targetParentId = list.dataset.parentId;
                
                if (draggedInfo && targetParentId) {
                    if (targetParentId === draggedInfo.parentId) return;
                    
                    const sourceItem = itemsData.find(i => i.id === draggedInfo.parentId);
                    const targetItem = itemsData.find(i => i.id === targetParentId);
                    
                    if (sourceItem && targetItem) {
                        const movedService = sourceItem.level2.splice(draggedInfo.itemIdx, 1)[0];
                        targetItem.level2.push(movedService);
                        updateStructureView();
                    }
                }
            });
        });
    }
});
