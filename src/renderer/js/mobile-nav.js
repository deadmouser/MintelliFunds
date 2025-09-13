// Mobile Navigation Handler
class MobileNavigation {
    constructor() {
        this.sidebar = null;
        this.overlay = null;
        this.menuBtn = null;
        this.isOpen = false;
        
        this.init();
    }
    
    init() {
        this.createMobileElements();
        this.bindEvents();
        this.handleResize();
        
        // Listen for window resize
        window.addEventListener('resize', () => this.handleResize());
    }
    
    createMobileElements() {
        // Create mobile header if it doesn't exist
        if (!document.querySelector('.mobile-header')) {
            this.createMobileHeader();
        }
        
        // Create overlay
        this.createOverlay();
        
        // Get sidebar reference
        this.sidebar = document.querySelector('.sidebar');
    }
    
    createMobileHeader() {
        const header = document.createElement('div');
        header.className = 'mobile-header';
        header.innerHTML = `
            <button class="mobile-menu-btn" aria-label="Toggle menu">
                <i class="fas fa-bars"></i>
            </button>
            <div class="mobile-title">Financial AI</div>
            <div class="mobile-actions">
                <button class="theme-toggle mobile" aria-label="Toggle theme">
                    <i class="fas fa-moon"></i>
                </button>
            </div>
        `;
        
        document.body.insertBefore(header, document.body.firstChild);
        
        // Get menu button reference
        this.menuBtn = header.querySelector('.mobile-menu-btn');
        
        // Initialize theme toggle for mobile
        const mobileThemeToggle = header.querySelector('.theme-toggle.mobile');
        if (window.themeManager && mobileThemeToggle) {
            mobileThemeToggle.addEventListener('click', () => {
                window.themeManager.toggleTheme();
            });
        }
    }
    
    createOverlay() {
        if (!document.querySelector('.sidebar-overlay')) {
            const overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            document.body.appendChild(overlay);
            this.overlay = overlay;
        } else {
            this.overlay = document.querySelector('.sidebar-overlay');
        }
    }
    
    bindEvents() {
        // Menu button click
        if (this.menuBtn) {
            this.menuBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleSidebar();
            });
        }
        
        // Overlay click
        if (this.overlay) {
            this.overlay.addEventListener('click', () => {
                this.closeSidebar();
            });
        }
        
        // Close on nav link click (mobile)
        if (this.sidebar) {
            this.sidebar.addEventListener('click', (e) => {
                if (e.target.matches('.nav-link') && window.innerWidth <= 768) {
                    this.closeSidebar();
                }
            });
        }
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeSidebar();
            }
        });
        
        // Handle touch gestures
        this.initTouchGestures();
    }
    
    initTouchGestures() {
        let startX = 0;
        let startY = 0;
        let isScrolling = false;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isScrolling = false;
        }, { passive: true });
        
        document.addEventListener('touchmove', (e) => {
            if (!startX || !startY) return;
            
            const diffX = e.touches[0].clientX - startX;
            const diffY = e.touches[0].clientY - startY;
            
            if (Math.abs(diffY) > Math.abs(diffX)) {
                isScrolling = true;
            }
        }, { passive: true });
        
        document.addEventListener('touchend', (e) => {
            if (!startX || isScrolling) return;
            
            const diffX = e.changedTouches[0].clientX - startX;
            const minSwipeDistance = 100;
            
            // Swipe right from left edge to open
            if (startX < 50 && diffX > minSwipeDistance && !this.isOpen) {
                this.openSidebar();
            }
            // Swipe left to close
            else if (diffX < -minSwipeDistance && this.isOpen) {
                this.closeSidebar();
            }
            
            startX = 0;
            startY = 0;
        }, { passive: true });
    }
    
    toggleSidebar() {
        if (this.isOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }
    
    openSidebar() {
        if (!this.sidebar) return;
        
        this.isOpen = true;
        this.sidebar.classList.add('open');
        
        if (this.overlay) {
            this.overlay.classList.add('visible');
        }
        
        // Update menu button icon
        const icon = this.menuBtn?.querySelector('i');
        if (icon) {
            icon.className = 'fas fa-times';
        }
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Focus management
        this.sidebar.setAttribute('aria-expanded', 'true');
        
        // Animate menu button
        if (this.menuBtn) {
            this.menuBtn.style.transform = 'rotate(90deg)';
        }
    }
    
    closeSidebar() {
        if (!this.sidebar) return;
        
        this.isOpen = false;
        this.sidebar.classList.remove('open');
        
        if (this.overlay) {
            this.overlay.classList.remove('visible');
        }
        
        // Update menu button icon
        const icon = this.menuBtn?.querySelector('i');
        if (icon) {
            icon.className = 'fas fa-bars';
        }
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Focus management
        this.sidebar.setAttribute('aria-expanded', 'false');
        
        // Animate menu button
        if (this.menuBtn) {
            this.menuBtn.style.transform = 'rotate(0deg)';
        }
    }
    
    handleResize() {
        const isMobile = window.innerWidth <= 768;
        const mobileHeader = document.querySelector('.mobile-header');
        
        if (isMobile) {
            // Show mobile header
            if (mobileHeader) {
                mobileHeader.style.display = 'flex';
            }
            
            // Close sidebar if open when switching to mobile
            if (this.isOpen && this.sidebar) {
                this.closeSidebar();
            }
        } else {
            // Hide mobile header on desktop
            if (mobileHeader) {
                mobileHeader.style.display = 'none';
            }
            
            // Ensure sidebar is properly positioned for desktop
            if (this.sidebar) {
                this.sidebar.classList.remove('open');
            }
            
            if (this.overlay) {
                this.overlay.classList.remove('visible');
            }
            
            // Restore body scroll
            document.body.style.overflow = '';
            
            this.isOpen = false;
        }
        
        // Update theme toggle icon in mobile header
        this.updateMobileThemeIcon();
    }
    
    updateMobileThemeIcon() {
        const mobileThemeToggle = document.querySelector('.mobile-header .theme-toggle i');
        if (!mobileThemeToggle) return;
        
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        mobileThemeToggle.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
    }
    
    // Public methods for external access
    isMenuOpen() {
        return this.isOpen;
    }
    
    forceClose() {
        this.closeSidebar();
    }
}

// Initialize mobile navigation when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mobileNav = new MobileNavigation();
});

// Export for other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileNavigation;
}