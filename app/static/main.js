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
        placeholder: "Buscar banco...",
        items: ['GLOBAL'],
        onChange: function(value) {
            updateTableRow(value);
        }
    })[0].selectize;

    const updateTableRow = (popValue) => {
        currentFilteredMAF = data.minor_allele_freq;
        if (popValue !== "GLOBAL") {
            const found = data.pop_frequencies.find(p => p.population === popValue);
            if (found) currentFilteredMAF = `${found.allele}: ${found.frequency.toFixed(4)}`;
        }

        tbody.innerHTML = `
            <tr class="animate-fade-up">
                <td>${data.rsid}</td>
                <td>${data.chromosome}</td>
                <td>${data.position}</td>
                <td><span class="badge bg-dark border border-secondary">${data.alleles}</span></td>
                <td class="text-warning fw-bold">${currentFilteredMAF}</td>
                <td><small>${data.genes.join(', ') || 'N/A'}</small></td>
                <td><span class="badge" style="background:var(--light-purple)">${data.consequence}</span></td>
            </tr>
        `;
    };

    // Configura botões de download para baixar o que está VISÍVEL
    const exportContainer = document.getElementById('export-buttons-container');
    exportContainer.innerHTML = ''; // Limpa botões antigos

    const btnClasses = "btn-export";
    
    // Botão JSON (Visível)
    const btnJson = document.createElement('button');
    btnJson.className = btnClasses;
    btnJson.innerText = 'JSON';
    btnJson.onclick = () => {
        const visibleData = { ...data, minor_allele_freq: currentFilteredMAF };
        downloadFile(JSON.stringify(visibleData, null, 2), `${data.rsid}.json`, 'application/json');
    };

    // Botão TSV (Visível)
    const btnTsv = document.createElement('button');
    btnTsv.className = btnClasses;
    btnTsv.innerText = 'TSV';
    btnTsv.onclick = () => {
        const content = `rsid\tchr\tpos\talleles\tmaf\tgenes\tconsequence\n${data.rsid}\t${data.chromosome}\t${data.position}\t${data.alleles}\t${currentFilteredMAF}\t${data.genes.join(',')}\t${data.consequence}`;
        downloadFile(content, `${data.rsid}.tsv`, 'text/tab-separated-values');
    };

    // Botão CSV (Visível)
    const btnCsv = document.createElement('button');
    btnCsv.className = btnClasses;
    btnCsv.innerText = 'CSV';
    btnCsv.onclick = () => {
        const content = `rsid,chr,pos,alleles,maf,genes,consequence\n${data.rsid},${data.chromosome},${data.position},${data.alleles},"${currentFilteredMAF}","${data.genes.join(',')}",${data.consequence}`;
        downloadFile(content, `${data.rsid}.csv`, 'text/csv');
    };

    exportContainer.append(btnJson, btnTsv, btnCsv);
    updateTableRow('GLOBAL');
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