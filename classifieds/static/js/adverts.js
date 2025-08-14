document.addEventListener('DOMContentLoaded', function() {
    const accountDropdown = document.querySelector('.account-dropdown');
    
    accountDropdown.addEventListener('mouseenter', function() {
        fetch('/get_user_adverts/')
            .then(response => response.json())
            .then(adverts => {
                const advertsList = document.getElementById('user-adverts-list');
                const countElement = document.getElementById('advert-count');
                
                countElement.textContent = adverts.length;
                advertsList.innerHTML = '';
                
                if (adverts.length === 0) {
                    advertsList.innerHTML = '<div class="no-adverts">No active adverts found</div>';
                } else {
                    adverts.forEach(advert => {
                        const advertElement = document.createElement('div');
                        advertElement.className = 'advert-item';
                        
                        let priceHtml = '';
                        if (advert.price) {
                            priceHtml = `<span class="advert-price">$${advert.price}</span>`;
                        }
                        
                        advertElement.innerHTML = `
                            <div class="advert-category-badge">${advert.category}</div>
                            <a href="/adverts/${advert.id}" class="advert-title">${advert.title}</a>
                            ${priceHtml}
                            <small class="advert-date">${advert.created_at}</small>
                        `;
                        advertsList.appendChild(advertElement);
                    });
                }
            });
    });
});