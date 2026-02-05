/**
 * Desafio Técnico - Analista de Bioinformática
 */

let lastVariantData = null;
let historyCache = JSON.parse(localStorage.getItem('genvar_recent_v2') || '[]');

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('rsid-input');
    const clearBtn = document.getElementById('clear-search');
    const dropdown = document.getElementById('history-dropdown');

    // 1. Gatilho de Busca (Enter)
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') buscarVariante();
    });

    // 2. Controle do Botão X e Histórico
    input.addEventListener('input', () => {
        const hasValue = input.value.length > 0;
        clearBtn.style.display = hasValue ? 'flex' : 'none';
        dropdown.style.display = 'none';
    });

    input.addEventListener('focus', () => {
        if (historyCache.length > 0 && !input.value) renderHistory();
    });

    clearBtn.addEventListener('click', () => {
        input.value = '';
        clearBtn.style.display = 'none';
        dropdown.style.display = 'none';
        input.focus();
    });

    // Fechar dropdown ao clicar fora
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
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'rsID não encontrado');

        lastVariantData = data;
        updateCache(data.rsid);
        renderHorizontalTable(data);
    } catch (err) {
        document.getElementById('status-area').innerHTML = `
            <div class="alert alert-danger border-0 mt-3"><i class="bi bi-exclamation-triangle me-2"></i>${err.message}</div>`;
    } finally {
        toggleProgress(false);
    }
}

/** Tabela, Selectize e Download Dinâmico */
function renderHorizontalTable(data) {
    const tbody = document.getElementById('table-body');
    const jsonViewer = document.getElementById('json-viewer');
    const $select = $('#pop-select');
    let currentFilteredMAF = data.minor_allele_freq;

    // Reinicia Selectize
    if ($select[0].selectize) $select[0].selectize.destroy();

    const selectOptions = data.pop_frequencies.map(p => ({ text: p.population, value: p.population }));

    const selectize = $select.selectize({
        options: [{ text: "Highest MAF (Global)", value: "GLOBAL" }, ...selectOptions],
        labelField: 'text',
        valueField: 'value',
        searchField: ['text'],
        placeholder: "Search population database...",
        items: ['GLOBAL'],
        onChange: function(value) {
            updateView(value);
        }
    })[0].selectize;

    /** Atualiza a Tabela e o Visualizador JSON simultaneamente */
    const updateView = (popValue) => {
        currentFilteredMAF = data.minor_allele_freq;
        let selectedPopData = data.minor_allele_freq; 

        if (popValue !== "GLOBAL") {
            const found = data.pop_frequencies.find(p => p.population === popValue);
            if (found) {
                // Arredondando para 2 casas como solicitado
                currentFilteredMAF = `${found.allele}: ${found.frequency.toFixed(2)}`;
                selectedPopData = currentFilteredMAF;
            }
        }

        // 1. Atualiza Tabela com alinhamentos específicos (Chr na direita, outros centralizados)
        tbody.innerHTML = `
            <tr class="animate-fade-up">
                <td class="text-center">${data.rsid}</td>
                <td class="text-end">${data.chromosome}</td>
                <td class="text-center">${data.position}</td>
                <td class="text-center"><span class="badge bg-dark border border-secondary">${data.alleles}</span></td>
                <td class="text-center text-info">${data.maf_1000g}</td>
                <td class="text-center text-warning fw-bold">${currentFilteredMAF}</td>
                <td class="text-center"><small>${data.genes.join(', ') || 'N/A'}</small></td>
                <td class="text-center"><span class="badge" style="background:var(--light-purple)">${data.consequence}</span></td>
            </tr>
        `;

        // 2. Atualiza Visualizador JSON com a ordem e nomes de chaves solicitados
        const visibleJson = {
            "rsid": data.rsid,
            "chromosome": data.chromosome,
            "position": data.position,
            "alleles": data.alleles,
            "minor_allele_freq": data.maf_1000g,
            "highest_minor_allele_freq_MAF": selectedPopData,
            "genes": data.genes,
            "consequence": data.consequence
        };
        jsonViewer.textContent = JSON.stringify(visibleJson, null, 2);
    };

    // Configura botões de download para baixar apenas o filtrado
    const exportContainer = document.getElementById('export-buttons-container');
    exportContainer.innerHTML = ''; 

    const btnClasses = "btn-export";
    
    // JSON Filtered
    const btnJson = document.createElement('button');
    btnJson.className = btnClasses;
    btnJson.innerText = 'JSON';
    btnJson.onclick = () => {
        const content = jsonViewer.textContent;
        downloadFile(content, `${data.rsid}.json`, 'application/json');
    };

    // TSV Filtered
    const btnTsv = document.createElement('button');
    btnTsv.className = btnClasses;
    btnTsv.innerText = 'TSV';
    btnTsv.onclick = () => {
        const header = "rsid\tchromosome\tposition\talleles\t1000g_maf\thighest_maf_source\tgenes\tconsequence\n";
        const content = `${data.rsid}\t${data.chromosome}\t${data.position}\t${data.alleles}\t${data.maf_1000g}\t${currentFilteredMAF}\t${data.genes.join(',')}\t${data.consequence}`;
        downloadFile(header + content, `${data.rsid}.tsv`, 'text/tab-separated-values');
    };

    // CSV Filtered
    const btnCsv = document.createElement('button');
    btnCsv.className = btnClasses;
    btnCsv.innerText = 'CSV';
    btnCsv.onclick = () => {
        const header = "rsid,chromosome,position,alleles,1000g_maf,highest_maf_source,genes,consequence\n";
        const content = `${data.rsid},${data.chromosome},${data.position},${data.alleles},"${data.maf_1000g}","${currentFilteredMAF}","${data.genes.join(',')}",${data.consequence}`;
        downloadFile(header + content, `${data.rsid}.csv`, 'text/csv');
    };

    exportContainer.append(btnJson, btnTsv, btnCsv);
    updateView('GLOBAL');
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
}

function updateCache(rsid) {
    historyCache = [rsid, ...historyCache.filter(i => i !== rsid)].slice(0, 5);
    localStorage.setItem('genvar_recent_v2', JSON.stringify(historyCache));
}

function toggleProgress(show) {
    const wrapper = document.getElementById('progress-wrapper');
    const bar = document.getElementById('progress-bar');
    if (show) { wrapper.classList.remove('d-none'); setTimeout(() => bar.style.width = '100%', 10); }
    else { bar.style.width = '100%'; setTimeout(() => { wrapper.classList.add('d-none'); bar.style.width = '0%'; }, 600); }
}