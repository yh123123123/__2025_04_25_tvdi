document.addEventListener('DOMContentLoaded', () => {
    const track = document.querySelector('.homes-for-you-section__carousel-track');
    const cards = Array.from(track.children);
    const nextButton = document.querySelector('.carousel-arrow--next');
    const prevButton = document.querySelector('.carousel-arrow--prev');
    const paginationContainer = document.querySelector('.carousel-pagination');

    let itemsPerPage = getItemsPerPage();
    const totalItems = cards.length;
    let totalPages = Math.ceil(totalItems / itemsPerPage);
    let currentIndex = 0;

    function getItemsPerPage() {
        if (window.innerWidth < 576) {
            return 1;
        } else if (window.innerWidth < 992) {
            return 2;
        } else {
            return 3;
        }
    }

    function updateItemsPerPage() {
        const newItemsPerPage = getItemsPerPage();
        if (newItemsPerPage !== itemsPerPage) {
            // Recalculate current page based on the first visible item
            const firstVisibleItemIndex = currentIndex * itemsPerPage;
            itemsPerPage = newItemsPerPage;
            totalPages = Math.ceil(totalItems / itemsPerPage);
            currentIndex = Math.floor(firstVisibleItemIndex / itemsPerPage);
            if (currentIndex >= totalPages) {
                currentIndex = totalPages - 1;
            }
            if (currentIndex < 0) currentIndex = 0; // Ensure currentIndex is not negative
            setupPagination();
            updateCarousel();
        }
    }


    function updateCarousel() {
        if (!track || cards.length === 0) return; // 安全檢查

        const cardStyle = window.getComputedStyle(cards[0]);
        const cardMarginRight = parseFloat(cardStyle.marginRight) || 0; // Fallback if not set, though gap is used
        const trackGap = parseFloat(window.getComputedStyle(track).gap) || 30; // 從 CSS 獲取 gap 值

        // 卡片寬度是軌道容器寬度除以每頁項目數，再減去相應的gap
        // 但由於 flex-basis 已處理寬度，這裡我們需要計算每張卡片的實際佔用寬度（包括gap）
        // flex-basis: calc(100% / N - (gap * (N-1) / N))
        // translateX 的計算應該基於 "一個滑動單位" 的寬度
        // 一個滑動單位 = (卡片寬度 + gap) * itemsPerPage
        // 或者更簡單：軌道容器的寬度

        const trackContainerWidth = track.parentElement.offsetWidth;
        const slideWidth = trackContainerWidth + trackGap; // 這是指整個可視區域的滑動寬度

        // 計算translateX的值，以移動 itemsPerPage 個卡片
        // 每個卡片的寬度 + gap 的總和乘以 currentIndex
        // translateX = -currentIndex * (一個完整頁面的寬度)
        // 一個完整頁面的寬度是 N 個卡片的寬度 + (N-1) 個 gap，但因為我們是滑動整個 viewport
        // 所以滑動距離是 currentIndex * (軌道容器寬度 + 一個 gap)
        // 這個 gap 是為了讓下一頁的第一張卡片正確對齊
        // 如果 track 內有 padding, 要考慮進去
        // const trackPaddingLeft = parseFloat(window.getComputedStyle(track).paddingLeft) || 0;

        // 滑動寬度：(卡片寬度 + gap) * itemsPerPage，但是我們只移動一個可視區塊
        // 滑動一個可視區塊，就是移動 trackContainerWidth + 一個 gap （這個 gap 是 trackContainer 邊緣與下一個卡片組的間隔）
        let offset = -currentIndex * (trackContainerWidth + trackGap);

        // 為了修正最後一頁可能不滿的情況，並且讓最後一個元素能正確顯示
        if (currentIndex === totalPages - 1) {
            // 如果是最後一頁，計算偏移量，使得最後的卡片能靠右對齊
            const remainingItems = totalItems - (currentIndex * itemsPerPage);
            const cardWidth = cards[0].offsetWidth; // 假設所有卡片等寬
            const lastPageVisibleWidth = (cardWidth * remainingItems) + (trackGap * (remainingItems - 1));
            const maxOffset = - (((cardWidth + trackGap) * totalItems - trackGap) - trackContainerWidth);

            if (totalItems % itemsPerPage !== 0 || itemsPerPage > 1) { // 只有當最後一頁不滿且每頁多於一張卡時才調整
                offset = -((cardWidth + trackGap) * (totalItems - itemsPerPage));
                // 如果總項目少於等於每頁項目，不需特殊調整，offset 應為 0
                if (totalItems <= itemsPerPage) {
                    offset = 0;
                } else {
                    // 確保不會滑過頭
                    const totalTrackWidth = cards.reduce((acc, card) => acc + card.offsetWidth, 0) + trackGap * (totalItems - 1);
                    const maxPossibleOffset = -(totalTrackWidth - trackContainerWidth + (parseFloat(window.getComputedStyle(track).paddingLeft) || 0) + (parseFloat(window.getComputedStyle(track).paddingRight) || 0));
                    if (offset < maxPossibleOffset && totalTrackWidth > trackContainerWidth) {
                        offset = maxPossibleOffset;
                    } else if (totalTrackWidth <= trackContainerWidth) {
                        offset = 0; // 如果所有卡片都能塞滿，就不滑動
                    }
                }
            }
            // 特殊處理只有一頁的情況，不滑動
            if (totalPages === 1) {
                offset = 0;
            }
        }


        track.style.transform = `translateX(${offset}px)`;

        updatePaginationDots();
        updateArrowStates();
    }

    function setupPagination() {
        if (!paginationContainer) return;
        paginationContainer.innerHTML = ''; // 清空舊的點
        totalPages = Math.ceil(totalItems / itemsPerPage); // 重新計算總頁數

        if (totalPages <= 1) { // 如果只有一頁或沒有頁面，不顯示分頁點
            paginationContainer.style.display = 'none';
            return;
        }
        paginationContainer.style.display = 'flex';


        for (let i = 0; i < totalPages; i++) {
            const dot = document.createElement('button');
            dot.classList.add('carousel-pagination__dot');
            dot.setAttribute('aria-label', `Go to page ${i + 1}`);
            dot.addEventListener('click', () => {
                currentIndex = i;
                updateCarousel();
            });
            paginationContainer.appendChild(dot);
        }
        updatePaginationDots();
    }

    function updatePaginationDots() {
        if (!paginationContainer) return;
        const dots = Array.from(paginationContainer.children);
        dots.forEach((dot, index) => {
            if (index === currentIndex) {
                dot.classList.add('carousel-pagination__dot--active');
                dot.setAttribute('aria-current', 'true');
            } else {
                dot.classList.remove('carousel-pagination__dot--active');
                dot.removeAttribute('aria-current');
            }
        });
    }

    function updateArrowStates() {
        if (!prevButton || !nextButton) return;
        prevButton.disabled = currentIndex === 0;
        nextButton.disabled = currentIndex >= totalPages - 1;
    }

    nextButton.addEventListener('click', () => {
        if (currentIndex < totalPages - 1) {
            currentIndex++;
            updateCarousel();
        }
    });

    prevButton.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    });

    window.addEventListener('resize', () => {
        updateItemsPerPage();
        // No need to call updateCarousel() here as updateItemsPerPage will call it if necessary.
    });

    // 初始化
    if (totalItems > 0) {
        setupPagination();
        updateCarousel(); // 初始加載時更新輪播狀態
    } else {
        // 如果沒有卡片，隱藏導航和分頁
        if (nextButton) nextButton.style.display = 'none';
        if (prevButton) prevButton.style.display = 'none';
        if (paginationContainer) paginationContainer.style.display = 'none';
    }
});