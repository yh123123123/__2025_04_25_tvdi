// script.js
document.addEventListener('DOMContentLoaded', () => {
    const tabComponents = document.querySelectorAll('.course-category-tabs');

    tabComponents.forEach(tabComponent => {
        const tabContainer = tabComponent.querySelector('.tab-container');
        if (!tabContainer) {
            console.error('Tab container not found within:', tabComponent);
            return;
        }

        const tabs = tabContainer.querySelectorAll('.tab-button');

        if (tabs.length === 0) {
            console.warn('No tab buttons found in:', tabContainer);
            return;
        }

        // Set initial active tab's ARIA attributes correctly if not already set
        tabs.forEach(tab => {
            if (tab.classList.contains('active')) {
                tab.setAttribute('aria-selected', 'true');
            } else {
                tab.setAttribute('aria-selected', 'false');
            }
        });

        tabContainer.addEventListener('click', (event) => {
            const clickedTab = event.target.closest('.tab-button');

            if (!clickedTab || !tabContainer.contains(clickedTab)) {
                // Click was not on a tab button or was outside the designated container
                return;
            }

            // If the clicked tab is already active, do nothing
            if (clickedTab.classList.contains('active')) {
                return;
            }

            // Remove 'active' class and set aria-selected to false for all tabs in this component
            tabs.forEach(tab => {
                tab.classList.remove('active');
                tab.setAttribute('aria-selected', 'false');
            });

            // Add 'active' class and set aria-selected to true for the clicked tab
            clickedTab.classList.add('active');
            clickedTab.setAttribute('aria-selected', 'true');

            // Dispatch custom event with the selected category
            const category = clickedTab.dataset.category;
            if (category) {
                const categoryChangeEvent = new CustomEvent('categoryChange', {
                    detail: { category: category },
                    bubbles: true, // Allows the event to bubble up the DOM tree
                    composed: true // Allows the event to cross Shadow DOM boundaries (if used later)
                });
                // Dispatch from the main component element for easier listening
                tabComponent.dispatchEvent(categoryChangeEvent);
            } else {
                console.warn('Clicked tab does not have a data-category attribute:', clickedTab);
            }
        });

        // RWD Detection and Adaptation (if needed beyond CSS)
        // The current requirements are mostly handled by CSS media queries.
        // This section could be used if JavaScript needs to react to breakpoint changes,
        // e.g., re-calculating layouts or loading different content, which is not specified here.
        // For now, CSS handles the responsive styling changes.
        // Example:
        // const handleResize = () => {
        //     if (window.innerWidth < 768) {
        //         // Mobile-specific JS logic
        //     } else {
        //         // Desktop/Tablet specific JS logic
        //     }
        // };
        // window.addEventListener('resize', handleResize);
        // handleResize(); // Initial check
    });
});