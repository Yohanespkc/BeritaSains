// NeuralGen Portal App Script

document.addEventListener('DOMContentLoaded', () => {
    // State management
    let newsData = {
        last_updated: null,
        articles: []
    };
    let activeCategory = 'all';
    let searchQuery = '';

    // DOM Elements
    const newsFeed = document.getElementById('news-feed');
    const updateBadge = document.getElementById('update-badge');
    const searchInput = document.getElementById('search-input');
    const clearSearchBtn = document.getElementById('clear-search');
    const tabButtons = document.querySelectorAll('.tab-btn');
    
    // Modal Elements
    const modal = document.getElementById('detail-modal');
    const modalContent = modal.querySelector('.modal-content');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalCategory = document.getElementById('modal-category');
    const modalTitle = document.getElementById('modal-title');
    const modalOriginalTitle = document.getElementById('modal-original-title');
    const modalSource = document.getElementById('modal-source');
    const modalDate = document.getElementById('modal-date');
    const modalSummary = document.getElementById('modal-summary');
    const modalTakeaways = document.getElementById('modal-takeaways');
    const modalUrl = document.getElementById('modal-url');

    // Months translation array
    const MONTHS = [
        'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ];

    // Helper: Format ISO date string into Indonesian readable format (e.g. 19 Juli 2026)
    function formatIndonesianDate(dateStr) {
        if (!dateStr) return '';
        try {
            const parts = dateStr.split('-');
            if (parts.length === 3) {
                const year = parts[0];
                const monthIdx = parseInt(parts[1], 10) - 1;
                const day = parseInt(parts[2], 10);
                if (monthIdx >= 0 && monthIdx < 12) {
                    return `${day} ${MONTHS[monthIdx]} ${year}`;
                }
            }
            // Fallback
            const d = new Date(dateStr);
            if (!isNaN(d.getTime())) {
                return `${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()}`;
            }
            return dateStr;
        } catch (e) {
            return dateStr;
        }
    }

    // Helper: Get human readable relative time or time string for "Last Updated"
    function formatLastUpdated(isoString) {
        if (!isoString) return 'Belum pernah diperbarui';
        try {
            const date = new Date(isoString);
            const now = new Date();
            const diffMs = now - date;
            const diffMin = Math.floor(diffMs / 60000);
            const diffHrs = Math.floor(diffMin / 60);

            // Format Jam & Menit
            const pad = (num) => String(num).padStart(2, '0');
            const timeStr = `${pad(date.getHours())}:${pad(date.getMinutes())}`;

            if (diffMin < 1) return 'Diperbarui baru saja';
            if (diffMin < 60) return `Diperbarui ${diffMin} menit yang lalu`;
            if (diffHrs < 24) return `Diperbarui ${diffHrs} jam yang lalu (${timeStr} WIB)`;
            
            return `Terakhir Diperbarui: ${date.getDate()} ${MONTHS[date.getMonth()]} ${date.getFullYear()} pukul ${timeStr} WIB`;
        } catch (e) {
            return 'Terakhir Diperbarui: Baru-baru ini';
        }
    }

    // Category style mapping
    function getCategoryClass(category) {
        switch (category) {
            case 'Artificial Intelligence':
                return 'cat-ai';
            case 'Genom & Biotek':
                return 'cat-genom';
            default:
                return 'cat-scitech';
        }
    }

    // Load data from news.json
    async function loadNews() {
        showLoading();
        try {
            // Fetch database JSON
            const response = await fetch('data/news.json');
            if (!response.ok) {
                throw new Error('Database file not found or failed to load');
            }
            const data = await response.json();
            
            newsData.last_updated = data.last_updated;
            newsData.articles = data.articles || [];
            
            updateStatusBadge(newsData.last_updated);
            renderNews();
        } catch (error) {
            console.error('Error loading news database:', error);
            showError(`Gagal memuat berita: ${error.message}. Pastikan Anda telah menjalankan scraper atau terdapat file data/news.json.`);
        }
    }

    // Update the last updated status badge at the top
    function updateStatusBadge(lastUpdated) {
        const textElement = updateBadge.querySelector('.status-text');
        textElement.textContent = formatLastUpdated(lastUpdated);
    }

    // Filter and Search Logic
    function getFilteredArticles() {
        return newsData.articles.filter(article => {
            // Category Match
            const categoryMatch = activeCategory === 'all' || article.category === activeCategory;
            
            // Search Match
            const searchLower = searchQuery.toLowerCase();
            const searchMatch = !searchQuery || 
                (article.title && article.title.toLowerCase().includes(searchLower)) ||
                (article.original_title && article.original_title.toLowerCase().includes(searchLower)) ||
                (article.summary && article.summary.toLowerCase().includes(searchLower)) ||
                (article.source && article.source.toLowerCase().includes(searchLower));
                
            return categoryMatch && searchMatch;
        });
    }

    // Render articles in feed
    function renderNews() {
        const filtered = getFilteredArticles();
        newsFeed.innerHTML = '';
        
        if (filtered.length === 0) {
            showEmpty();
            return;
        }

        // Group articles by published date for clean feed timeline
        const grouped = {};
        filtered.forEach(article => {
            const date = article.published_date || 'Lainnya';
            if (!grouped[date]) {
                grouped[date] = [];
            }
            grouped[date].push(article);
        });

        // Get sorted dates (descending)
        const sortedDates = Object.keys(grouped).sort((a, b) => b.localeCompare(a));

        sortedDates.forEach(dateStr => {
            // Add Date Section Divider
            const dateHeader = document.createElement('div');
            dateHeader.className = 'date-divider';
            dateHeader.textContent = dateStr === 'Lainnya' ? 'Lainnya' : formatIndonesianDate(dateStr);
            newsFeed.appendChild(dateHeader);

            // Add Cards under this date
            grouped[dateStr].forEach(article => {
                const card = document.createElement('article');
                card.className = 'news-card card-blur';
                card.setAttribute('data-category', article.category);
                
                const catClass = getCategoryClass(article.category);
                
                card.innerHTML = `
                    <div class="card-header">
                        <span class="card-category ${catClass}">${article.category}</span>
                        <span class="card-meta-date font-space">${formatIndonesianDate(article.published_date)}</span>
                    </div>
                    <div class="card-body">
                        <h3 class="card-title">${article.title}</h3>
                        <p class="card-summary">${article.summary}</p>
                    </div>
                    <div class="card-footer">
                        <span class="card-source">${article.source}</span>
                        <span class="read-more-link">
                            Detail
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                        </span>
                    </div>
                `;
                
                // Add event listener to open detailed modal
                card.addEventListener('click', () => openModal(article));
                
                newsFeed.appendChild(card);
            });
        });
    }

    // Modal Interactions
    function openModal(article) {
        modalCategory.textContent = article.category;
        
        // Remove old classes and add new category styling class
        modalCategory.className = 'modal-category';
        const catClass = getCategoryClass(article.category);
        modalCategory.classList.add(catClass);
        
        modalContent.setAttribute('data-category', article.category);

        modalTitle.textContent = article.title;
        modalOriginalTitle.textContent = article.original_title || '';
        modalSource.textContent = article.source || 'Sumber';
        modalDate.textContent = formatIndonesianDate(article.published_date);
        modalSummary.textContent = article.summary;

        // Render takeaways
        modalTakeaways.innerHTML = '';
        if (article.takeaways && Array.isArray(article.takeaways)) {
            article.takeaways.forEach(point => {
                const li = document.createElement('li');
                li.textContent = point;
                modalTakeaways.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'Tidak ada poin kesimpulan tambahan.';
            modalTakeaways.appendChild(li);
        }

        modalUrl.href = article.url || '#';

        // Display Modal
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Lock background scroll
    }

    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = ''; // Restore scroll
    }

    // UI State Helpers
    function showLoading() {
        newsFeed.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Mengambil berita terbaru...</p>
            </div>
        `;
    }

    function showError(message) {
        newsFeed.innerHTML = `
            <div class="error-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="red" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                <h3 style="margin-top: 16px; margin-bottom: 8px;">Terjadi Kesalahan</h3>
                <p>${message}</p>
            </div>
        `;
    }

    function showEmpty() {
        newsFeed.innerHTML = `
            <div class="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>
                <h3>Tidak Ada Hasil</h3>
                <p>Tidak menemukan berita yang cocok dengan filter atau kata kunci "${searchQuery}". Coba kata kunci lainnya.</p>
            </div>
        `;
    }

    // ==========================================
    // EVENT LISTENERS
    // ==========================================

    // Category Tabs click handlers
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            activeCategory = button.getAttribute('data-category');
            renderNews();
        });
    });

    // Search input handler
    searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        if (searchQuery.length > 0) {
            clearSearchBtn.style.display = 'block';
        } else {
            clearSearchBtn.style.display = 'none';
        }
        renderNews();
    });

    // Clear Search click handler
    clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        searchQuery = '';
        clearSearchBtn.style.display = 'none';
        searchInput.focus();
        renderNews();
    });

    // Modal close click handlers
    modalCloseBtn.addEventListener('click', closeModal);
    
    // Close modal if user clicks outside of the modal box
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Close modal with ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });

    // Initial load
    loadNews();
});
