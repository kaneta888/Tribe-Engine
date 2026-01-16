// Main JS for Antigravity

function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

document.addEventListener('DOMContentLoaded', () => {
    // Handle Like/Save AJAX
    document.body.addEventListener('click', async (e) => {
        const btn = e.target.closest('.ajax-toggle-btn');
        if (!btn) return;

        e.preventDefault();

        const type = btn.dataset.type; // 'like' or 'save'
        const postId = btn.dataset.postId;
        const url = btn.dataset.url;

        // Optimistic UI state
        const currentActive = btn.dataset.active === 'true';
        const newActive = !currentActive;

        // Save previous state for rollback
        const prevHtml = btn.innerHTML;
        const prevActive = btn.dataset.active;
        const prevColor = btn.style.color;

        // Apply Optimistic UI
        btn.dataset.active = newActive;
        const svg = btn.querySelector('svg');
        const countSpan = btn.querySelector('.count-span');

        if (type === 'like') {
            btn.style.color = newActive ? '#e74c3c' : 'var(--text-color)';
            if (svg) svg.setAttribute('fill', newActive ? 'currentColor' : 'none');
            if (countSpan) {
                let count = parseInt(countSpan.textContent);
                countSpan.textContent = newActive ? count + 1 : count - 1;
            }
        } else if (type === 'save') {
            btn.style.color = newActive ? 'var(--accent)' : 'var(--text-muted)';
            if (svg) svg.setAttribute('fill', newActive ? 'currentColor' : 'none');
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();

            if (data.status === 'success') {
                // Sync with server data if needed
                if (type === 'like' && countSpan) {
                    countSpan.textContent = data.like_count;
                }
                btn.dataset.active = (type === 'like' ? data.is_liked : data.is_saved);
            } else {
                throw new Error(data.message || 'Error occurred');
            }

        } catch (err) {
            console.error(err);
            // Rollback UI
            btn.innerHTML = prevHtml;
            btn.dataset.active = prevActive;
            btn.style.color = prevColor;
            showToast('エラーが発生しました。接続を確認してください。', 'error');
        }
    });
});
