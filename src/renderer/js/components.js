// Advanced UI Components
class UIComponents {
    constructor() {
        this.activeModals = new Set();
        this.tooltips = new Map();
        this.init();
    }

    init() {
        this.createModalContainer();
        this.createTooltipContainer();
        this.setupGlobalEventListeners();
    }

    createModalContainer() {
        if (!document.getElementById('modal-container')) {
            const container = document.createElement('div');
            container.id = 'modal-container';
            container.className = 'modal-container';
            document.body.appendChild(container);
        }
    }

    createTooltipContainer() {
        if (!document.getElementById('tooltip-container')) {
            const container = document.createElement('div');
            container.id = 'tooltip-container';
            container.className = 'tooltip-container';
            document.body.appendChild(container);
        }
    }

    setupGlobalEventListeners() {
        // Close modals on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModals.size > 0) {
                this.closeTopModal();
            }
        });

        // Setup tooltip triggers
        this.setupTooltips();
    }

    // Modal System
    createModal(options = {}) {
        const {
            title = 'Modal',
            content = '',
            size = 'medium', // small, medium, large, fullscreen
            closable = true,
            buttons = [],
            className = '',
            onShow = null,
            onHide = null
        } = options;

        const modalId = 'modal-' + Date.now() + Math.random().toString(36).substr(2, 9);
        
        const modal = document.createElement('div');
        modal.className = `modal modal-${size} ${className}`;
        modal.id = modalId;
        modal.innerHTML = `
            <div class="modal-overlay"></div>
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3 class="modal-title">${title}</h3>
                        ${closable ? '<button class="modal-close" aria-label="Close modal"><i class="fas fa-times"></i></button>' : ''}
                    </div>
                    <div class="modal-body">
                        ${typeof content === 'string' ? content : ''}
                    </div>
                    ${buttons.length > 0 ? `<div class="modal-footer">${this.renderModalButtons(buttons, modalId)}</div>` : ''}
                </div>
            </div>
        `;

        // Add to container
        document.getElementById('modal-container').appendChild(modal);
        
        // Add to active modals
        this.activeModals.add(modalId);

        // Setup event listeners
        if (closable) {
            const closeBtn = modal.querySelector('.modal-close');
            const overlay = modal.querySelector('.modal-overlay');
            
            [closeBtn, overlay].forEach(element => {
                if (element) {
                    element.addEventListener('click', () => this.closeModal(modalId));
                }
            });
        }

        // Add custom content if it's an element
        if (typeof content !== 'string' && content instanceof HTMLElement) {
            modal.querySelector('.modal-body').appendChild(content);
        }

        // Show modal with animation
        requestAnimationFrame(() => {
            modal.classList.add('modal-show');
            if (onShow) onShow(modal);
        });

        return {
            id: modalId,
            element: modal,
            close: () => this.closeModal(modalId),
            setContent: (newContent) => {
                const body = modal.querySelector('.modal-body');
                if (typeof newContent === 'string') {
                    body.innerHTML = newContent;
                } else {
                    body.innerHTML = '';
                    body.appendChild(newContent);
                }
            }
        };
    }

    renderModalButtons(buttons, modalId) {
        return buttons.map(button => {
            const {
                text = 'Button',
                className = 'btn-secondary',
                action = null,
                closeModal = true
            } = button;

            const btnId = 'btn-' + Date.now() + Math.random().toString(36).substr(2, 5);
            
            setTimeout(() => {
                const btnElement = document.getElementById(btnId);
                if (btnElement) {
                    btnElement.addEventListener('click', () => {
                        if (action) action();
                        if (closeModal) this.closeModal(modalId);
                    });
                }
            }, 0);

            return `<button id="${btnId}" class="btn ${className}">${text}</button>`;
        }).join('');
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.add('modal-hide');
        
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
            this.activeModals.delete(modalId);
        }, 300);
    }

    closeTopModal() {
        if (this.activeModals.size === 0) return;
        const topModalId = Array.from(this.activeModals).pop();
        this.closeModal(topModalId);
    }

    closeAllModals() {
        Array.from(this.activeModals).forEach(modalId => {
            this.closeModal(modalId);
        });
    }

    // Confirmation Dialog
    confirm(options = {}) {
        const {
            title = 'Confirm Action',
            message = 'Are you sure?',
            confirmText = 'Confirm',
            cancelText = 'Cancel',
            type = 'warning' // success, warning, danger, info
        } = options;

        return new Promise((resolve) => {
            const modal = this.createModal({
                title,
                content: `
                    <div class="confirm-dialog confirm-${type}">
                        <div class="confirm-icon">
                            <i class="fas ${this.getConfirmIcon(type)}"></i>
                        </div>
                        <p class="confirm-message">${message}</p>
                    </div>
                `,
                size: 'small',
                buttons: [
                    {
                        text: cancelText,
                        className: 'btn-secondary',
                        action: () => resolve(false)
                    },
                    {
                        text: confirmText,
                        className: `btn-${type === 'danger' ? 'danger' : 'primary'}`,
                        action: () => resolve(true)
                    }
                ]
            });
        });
    }

    getConfirmIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            warning: 'fa-exclamation-triangle',
            danger: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    // Alert Dialog
    alert(message, title = 'Alert', type = 'info') {
        return this.createModal({
            title,
            content: `
                <div class="alert-dialog alert-${type}">
                    <div class="alert-icon">
                        <i class="fas ${this.getConfirmIcon(type)}"></i>
                    </div>
                    <p class="alert-message">${message}</p>
                </div>
            `,
            size: 'small',
            buttons: [
                {
                    text: 'OK',
                    className: 'btn-primary'
                }
            ]
        });
    }

    // Tooltip System
    setupTooltips() {
        // Setup tooltips for elements with data-tooltip attribute
        document.addEventListener('mouseenter', (e) => {
            const target = e.target.closest('[data-tooltip]');
            if (target && !target.hasAttribute('data-tooltip-active')) {
                this.showTooltip(target);
            }
        });

        document.addEventListener('mouseleave', (e) => {
            const target = e.target.closest('[data-tooltip]');
            if (target) {
                this.hideTooltip(target);
            }
        });
    }

    showTooltip(element) {
        const text = element.getAttribute('data-tooltip');
        const position = element.getAttribute('data-tooltip-position') || 'top';
        
        if (!text) return;

        const tooltip = document.createElement('div');
        tooltip.className = `tooltip tooltip-${position}`;
        tooltip.textContent = text;

        document.getElementById('tooltip-container').appendChild(tooltip);
        element.setAttribute('data-tooltip-active', 'true');
        this.tooltips.set(element, tooltip);

        // Position tooltip
        this.positionTooltip(tooltip, element, position);

        // Show with animation
        requestAnimationFrame(() => {
            tooltip.classList.add('tooltip-show');
        });
    }

    hideTooltip(element) {
        const tooltip = this.tooltips.get(element);
        if (!tooltip) return;

        tooltip.classList.add('tooltip-hide');
        element.removeAttribute('data-tooltip-active');
        
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
            this.tooltips.delete(element);
        }, 200);
    }

    positionTooltip(tooltip, element, position) {
        const elementRect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();

        let top, left;

        switch (position) {
            case 'top':
                top = elementRect.top - tooltipRect.height - 8;
                left = elementRect.left + (elementRect.width - tooltipRect.width) / 2;
                break;
            case 'bottom':
                top = elementRect.bottom + 8;
                left = elementRect.left + (elementRect.width - tooltipRect.width) / 2;
                break;
            case 'left':
                top = elementRect.top + (elementRect.height - tooltipRect.height) / 2;
                left = elementRect.left - tooltipRect.width - 8;
                break;
            case 'right':
                top = elementRect.top + (elementRect.height - tooltipRect.height) / 2;
                left = elementRect.right + 8;
                break;
            default:
                top = elementRect.top - tooltipRect.height - 8;
                left = elementRect.left + (elementRect.width - tooltipRect.width) / 2;
        }

        // Keep tooltip within viewport
        top = Math.max(8, Math.min(top, window.innerHeight - tooltipRect.height - 8));
        left = Math.max(8, Math.min(left, window.innerWidth - tooltipRect.width - 8));

        tooltip.style.top = top + 'px';
        tooltip.style.left = left + 'px';
    }

    // Loading Spinner
    showLoading(container, message = 'Loading...') {
        const spinner = document.createElement('div');
        spinner.className = 'loading-overlay';
        spinner.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <p class="loading-message">${message}</p>
            </div>
        `;

        if (typeof container === 'string') {
            container = document.getElementById(container) || document.querySelector(container);
        }

        if (container) {
            container.style.position = 'relative';
            container.appendChild(spinner);
        }

        return {
            hide: () => {
                if (spinner.parentNode) {
                    spinner.classList.add('loading-hide');
                    setTimeout(() => {
                        if (spinner.parentNode) {
                            spinner.parentNode.removeChild(spinner);
                        }
                    }, 300);
                }
            }
        };
    }

    // Progress Bar
    createProgressBar(container, options = {}) {
        const {
            value = 0,
            max = 100,
            showValue = true,
            className = '',
            animated = true
        } = options;

        const progressBar = document.createElement('div');
        progressBar.className = `progress-bar ${className} ${animated ? 'progress-animated' : ''}`;
        
        const percentage = (value / max) * 100;
        
        progressBar.innerHTML = `
            <div class="progress-track">
                <div class="progress-fill" style="width: ${percentage}%"></div>
            </div>
            ${showValue ? `<div class="progress-value">${Math.round(percentage)}%</div>` : ''}
        `;

        if (typeof container === 'string') {
            container = document.getElementById(container) || document.querySelector(container);
        }

        if (container) {
            container.appendChild(progressBar);
        }

        return {
            element: progressBar,
            setValue: (newValue) => {
                const newPercentage = (newValue / max) * 100;
                const fill = progressBar.querySelector('.progress-fill');
                const valueEl = progressBar.querySelector('.progress-value');
                
                if (fill) fill.style.width = newPercentage + '%';
                if (valueEl) valueEl.textContent = Math.round(newPercentage) + '%';
            },
            destroy: () => {
                if (progressBar.parentNode) {
                    progressBar.parentNode.removeChild(progressBar);
                }
            }
        };
    }
}

// Create global instance
const uiComponents = new UIComponents();