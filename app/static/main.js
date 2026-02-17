/**
 * Desafio Técnico - Analista de Bioinformática
 * 
 */

let lastVariantData = null;
let historyCache = JSON.parse(localStorage.getItem('genvar_recent_v2') || '[]');

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('rsid-input');
    const clearBtn = document.getElementById('clear-search');
    const dropdown = document.getElementById('history-dropdown');

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') buscarVariante();
    });

    input.addEventListener('input', () => {
    const hasValue = input.value.length > 0;
    
    // Controla o botão de limpar (X)
    clearBtn.style.display = hasValue ? 'flex' : 'none';
    
    if (!hasValue) {
        // Se o campo estiver vazio (Backspace total)
        if (historyCache.length > 0) {
            renderHistory(); 
        } else {
            dropdown.style.display = 'none';
        }
    } else {
        // Se o usuário começou a digitar algo novo, esconde o histórico
        dropdown.style.display = 'none';
    }
});

    clearBtn.addEventListener('click', () => {
        input.value = '';
        clearBtn.style.display = 'none';
        dropdown.style.display = 'none';
        input.focus();
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) dropdown.style.display = 'none';
    });
});

/** Gerenciamento do Histórico */
function renderHistory() {
    const dropdown = document.getElementById('history-dropdown');
    if (historyCache.length === 0) return;

    dropdown.innerHTML = historyCache.map(rsid => `
        <div class="history-item d-flex justify-content-between align-items-center">
            <span onclick="selectFromHistory('${rsid}')" class="flex-grow-1 p-2" style="cursor:pointer">
                <i class="bi bi-clock-history me-2 text-white-50"></i> ${rsid}
            </span>
            <button class="btn-remove-history-item" onclick="removeFromHistory(event, '${rsid}')">
                <i class="bi bi-x"></i>
            </button>
        </div>
    `).join('');
    dropdown.style.display = 'block';
}

function selectFromHistory(rsid) {
    document.getElementById('rsid-input').value = rsid;
    document.getElementById('history-dropdown').style.display = 'none';
    document.getElementById('clear-search').style.display = 'flex';
    buscarVariante();
}

function removeFromHistory(event, rsid) {
    event.stopPropagation();
    historyCache = historyCache.filter(item => item !== rsid);
    localStorage.setItem('genvar_recent_v2', JSON.stringify(historyCache));
    renderHistory();
}

/** Busca API */
async function buscarVariante() {
    const input = document.getElementById('rsid-input');
    const rsid = input.value.trim();
    if (!rsid) return;

    toggleProgress(true);
    try {
        const response = await fetch(`/api/variant/${rsid}`);
        
        // Verifica se o servidor retornou erro 
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({})); 
            throw new Error(errorData.error || `Erro no servidor (Status: ${response.status})`);
        }

        const data = await response.json();

        // Se o backend retornou um objeto de erro formatado
        if (data.error) {
            throw new Error(data.error);
        }

        lastVariantData = data;
        updateCache(data.rsid);
        renderHorizontalTable(data);
        renderIdeogram(data); 
        
        document.getElementById('status-area').innerHTML = '';

    } catch (err) {
        console.error("Erro na busca:", err);
        
        let mensagemErro = err.message;
        
        if (err.message.includes("Unexpected token") || err.message.includes("503") || err.message.includes("504")) {
            mensagemErro = "O serviço Ensembl está instável ou fora do ar. Tentamos a conexão, mas não houve resposta a tempo.";
        } else if (err.message.includes("404")) {
            mensagemErro = "Variante não encontrada ou erro na comunicação com o servidor Ensembl.";
        }

        document.getElementById('status-area').innerHTML = `
            <div class="alert alert-warning border-0 mt-3">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                <strong>Nota:</strong> ${mensagemErro}
            </div>`;
    } finally {
        toggleProgress(false);
    }
}
/** Renderização do Ideogram */
function renderIdeogram(data) {
    document.getElementById('ideogram-container').innerHTML = '';
    new Ideogram({
        container: '#ideogram-container',
        organism: 'human',
        chromosomes: [data.chromosome],
        chrHeight: 480,
        chrWidth: 50,
        orientation: 'vertical',
        chrLabelSize: 14,
        annotations: [{
            name: data.rsid,
            chr: data.chromosome,
            start: data.position,
            stop: data.position,
            color: '#ff4d4d',
            shape: 'triangle'
        }],
        showBandLabels: true,
        chrLabelColor: '#fff',
        rotatable: false,
    });
}

/** Mapa com Pintura de Região e Zoom Dinâmico */
/** Mapa com Pintura de Região e Zoom Dinâmico */
function renderMap(data, lats, lons, names, isSpecific, isRegionArray) {
    const cleanLats = lats.map(n => parseFloat(n));
    const cleanLons = lons.map(n => parseFloat(n));

    const traces = names.map((name, i) => {
        const isRegion = isRegionArray && isRegionArray[i];
        
        // --- MELHORIA DE TAMANHO DINÂMICO ---
        // Se for região (isRegion), usamos um tamanho grande (80) para dar ideia de área.
        // Se for uma seleção específica (isSpecific) manual, usamos 22.
        // Para os pontos padrão do Global, usamos 18.
        const markerSize = isRegion ? 120 : (isSpecific ? 22 : 18);
        
        // Opacidade: 0.3 para regiões (permite ver o mapa embaixo) e 0.9 para pontos.
        const markerOpacity = isRegion ? 0.3 : 0.9;
        
        let markerColor = "#ff6d00"; // Padrão Global
        if (isSpecific) markerColor = "#240046"; 
        else if (i > 0) markerColor = "#9d4edd"; // Empates no global

        return {
            type: "scattermap",
            lat: [cleanLats[i]],
            lon: [cleanLons[i]],
            mode: "markers",
            name: String(name),
            marker: { 
                size: markerSize, 
                color: markerColor, 
                opacity: markerOpacity,
                line: { width: isRegion ? 0 : 2, color: 'white' }
            },
            hoverinfo: "text",
            text: [`${name}<br>MAF: ${data.minor_allele_freq}`]
        };
    });

    // Zoom Dinâmico: Se for região macro, abre mais o mapa para dar contexto
    let dynamicZoom = 2;
    if (names.length > 1) dynamicZoom = 1.5;
    else if (isRegionArray && isRegionArray[0]) dynamicZoom = 1.8;
    else if (isSpecific) dynamicZoom = 3.5;

    const layout = {
        showlegend: true,
        legend: { x: 1, xanchor: 'right', y: 1, bgcolor: 'rgba(255,255,255,0.9)' },
        map: {
            style: "carto-positron",
            center: { lat: cleanLats[0], lon: cleanLons[0] },
            zoom: dynamicZoom
        },
        margin: { r: 0, t: 0, b: 0, l: 0 }
    };

    Plotly.newPlot('map-container', traces, layout, { responsive: true, displayModeBar: false });
}

// Tabela, Selectize e Exportação 
function renderHorizontalTable(data) {
    const tbody = document.getElementById('table-body');
    const jsonViewer = document.getElementById('json-viewer');
    const $select = $('#pop-select');
    
    if ($select[0].selectize) $select[0].selectize.destroy();

    const selectOptions = data.pop_frequencies.map(p => ({ text: p.population, value: p.population }));

    $select.selectize({
        options: [{ text: "Highest MAF (Auto)", value: "GLOBAL" }, ...selectOptions],
        labelField: 'text',
        valueField: 'value',
        searchField: ['text'],
        items: ['GLOBAL'],
        dropdownParent: 'body',
        onChange: (value) => updateView(value)
    });

    const updateView = (popValue) => {
        let currentMAFDisplay = data.minor_allele_freq;
        let cLat, cLon, pName, isRegionArr;

        if (popValue === "GLOBAL") {
            cLat = data.highest_maf_lat; 
            cLon = data.highest_maf_lon;
            pName = data.highest_maf_labels; 
            isRegionArr = data.highest_maf_is_region;
        } else {
            const found = data.pop_frequencies.find(p => p.population === popValue);
            if (found) {
                currentMAFDisplay = `${found.allele}: ${found.frequency.toFixed(4)}`;
                cLat = [found.lat];
                cLon = [found.lon];
                // Usa o Label amigável do Python
                pName = [found.label || found.population];
                isRegionArr = [found.is_region];
            }
        }

        tbody.innerHTML = `
            <tr class="animate-fade-up">
                <td class="text-center">${data.rsid}</td>
                <td class="text-end">${data.chromosome}</td>
                <td class="text-center">${data.position}</td>
                <td class="text-center"><span class="badge bg-dark border border-secondary">${data.alleles}</span></td>
                <td class="text-center text-info">${data.maf_1000g}</td>
                <td class="text-center text-warning fw-bold">${currentMAFDisplay}</td>
                <td class="text-center"><small>${data.genes.join(', ')}</small></td>
                <td class="text-center"><span class="badge" style="background:var(--light-purple)">${data.consequence}</span></td>
            </tr>
        `;

        const rawJson = {
            "rsid": data.rsid,
            "chromosome": data.chromosome,
            "position": data.position,
            "alleles": data.alleles,
            "minor_allele_freq": data.maf_1000g,
            "highest_minor_allele_freq_MAF": currentMAFDisplay,
            "genes": data.genes,
            "consequence": data.consequence
        };
        jsonViewer.textContent = JSON.stringify(rawJson, null, 2);
        
        renderMap(data, cLat, cLon, pName, popValue !== "GLOBAL", isRegionArr);
    };

    const exportContainer = document.getElementById('export-buttons-container');
    exportContainer.innerHTML = ''; 
    ['JSON', 'TSV', 'CSV'].forEach(type => {
        const btn = document.createElement('button');
        btn.className = "btn-export";
        btn.innerText = type;
        btn.onclick = () => {
            let content = "";
            if (type === 'JSON') content = jsonViewer.textContent;
            else {
                const headers = "rsid,chr,pos,alleles,maf,genes,consequence\n";
                const row = `${data.rsid},${data.chromosome},${data.position},${data.alleles},${data.maf_1000g},${data.genes.join('|')},${data.consequence}`;
                content = type === 'TSV' ? headers.replace(/,/g, '\t') + row.replace(/,/g, '\t') : headers + row;
            }
            downloadFile(content, `${data.rsid}.${type.toLowerCase()}`, 'text/plain');
        };
        exportContainer.append(btn);
    });

    updateView('GLOBAL');
}

// Função para Download
function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
}

// Atualiza o cache
function updateCache(rsid) {
    historyCache = [rsid, ...historyCache.filter(i => i !== rsid)].slice(0, 5);
    localStorage.setItem('genvar_recent_v2', JSON.stringify(historyCache));
}

// Função de barra de progresso
function toggleProgress(show) {
    const wrapper = document.getElementById('progress-wrapper');
    const bar = document.getElementById('progress-bar');
    if (show) { wrapper.classList.remove('d-none'); setTimeout(() => bar.style.width = '100%', 10); }
    else { bar.style.width = '100%'; setTimeout(() => { wrapper.classList.add('d-none'); bar.style.width = '0%'; }, 600); }
}