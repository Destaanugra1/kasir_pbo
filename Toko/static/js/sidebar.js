/**
 * Sidebar JavaScript - Sistem Kasir Toko
 * Handles sidebar collapse/expand functionality, state persistence, and mobile interactions
 */

(function () {
  'use strict';

  // DOM Elements
  const elements = {
    sidebarToggle: document.getElementById('sidebarToggle'),
    mobileSidebar: document.getElementById('mobileSidebar'),
    closeSidebar: document.getElementById('closeSidebar'),
    desktopSidebar: document.getElementById('desktopSidebar'),
    sidebarCollapseToggle: document.getElementById('sidebarCollapseToggle'),
    toggleIcon: document.getElementById('toggleIcon'),
    mainContent: document.getElementById('mainContent'),
  };

  // State
  let isCollapsed = false;

  /**
   * Toggle sidebar collapse state
   */
  function toggleSidebarCollapse() {
    isCollapsed = !isCollapsed;

    if (isCollapsed) {
      elements.desktopSidebar.classList.add('sidebar-collapsed');
      elements.desktopSidebar.setAttribute('data-collapsed', 'true');
      elements.mainContent.classList.add('sidebar-collapsed');
      elements.toggleIcon.className = 'fas fa-chevron-right';
      elements.sidebarCollapseToggle.title = 'Expand Sidebar';
    } else {
      elements.desktopSidebar.classList.remove('sidebar-collapsed');
      elements.desktopSidebar.setAttribute('data-collapsed', 'false');
      elements.mainContent.classList.remove('sidebar-collapsed');
      elements.toggleIcon.className = 'fas fa-chevron-left';
      elements.sidebarCollapseToggle.title = 'Collapse Sidebar';
    }

    // Save state to localStorage
    localStorage.setItem('sidebarCollapsed', isCollapsed);

    // Trigger custom event for other components that might need to know about sidebar state
    window.dispatchEvent(
      new CustomEvent('sidebarToggle', {
        detail: { isCollapsed: isCollapsed },
      })
    );
  }

  /**
   * Load saved sidebar state from localStorage
   */
  function loadSidebarState() {
    const savedState = localStorage.getItem('sidebarCollapsed');
    if (savedState === 'true') {
      isCollapsed = false; // Set to false so toggle will make it true
      toggleSidebarCollapse();
    }
  }

  /**
   * Initialize desktop sidebar functionality
   */
  function initDesktopSidebar() {
    if (!elements.desktopSidebar || !elements.sidebarCollapseToggle) {
      return;
    }

    // Load saved state
    loadSidebarState();

    // Add click event listener
    elements.sidebarCollapseToggle.addEventListener(
      'click',
      toggleSidebarCollapse
    );

    // Add pulse animation on page load to draw attention
    setTimeout(() => {
      elements.sidebarCollapseToggle.classList.add('pulse');
      setTimeout(() => {
        elements.sidebarCollapseToggle.classList.remove('pulse');
      }, 4000); // Remove after 4 seconds
    }, 1000); // Start after 1 second
  }

  /**
   * Toggle mobile sidebar visibility
   */
  function toggleMobileSidebar() {
    if (elements.mobileSidebar) {
      elements.mobileSidebar.classList.toggle('-translate-x-full');
    }
  }

  /**
   * Close mobile sidebar
   */
  function closeMobileSidebar() {
    if (elements.mobileSidebar) {
      elements.mobileSidebar.classList.add('-translate-x-full');
    }
  }

  /**
   * Initialize mobile sidebar functionality
   */
  function initMobileSidebar() {
    // Mobile sidebar toggle
    if (elements.sidebarToggle && elements.mobileSidebar) {
      elements.sidebarToggle.addEventListener('click', toggleMobileSidebar);
    }

    // Close sidebar button
    if (elements.closeSidebar && elements.mobileSidebar) {
      elements.closeSidebar.addEventListener('click', closeMobileSidebar);
    }

    // Close sidebar when clicking outside
    document.addEventListener('click', (e) => {
      if (
        elements.mobileSidebar &&
        elements.sidebarToggle &&
        !elements.mobileSidebar.contains(e.target) &&
        !elements.sidebarToggle.contains(e.target)
      ) {
        closeMobileSidebar();
      }
    });
  }

  /**
   * Initialize keyboard shortcuts
   */
  function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl + B to toggle sidebar (desktop)
      if (e.ctrlKey && e.key === 'b' && elements.desktopSidebar) {
        e.preventDefault();
        toggleSidebarCollapse();
      }

      // Escape to close mobile sidebar
      if (e.key === 'Escape' && elements.mobileSidebar) {
        closeMobileSidebar();
      }
    });
  }

  /**
   * Handle window resize events
   */
  function initResizeHandler() {
    let resizeTimeout;

    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        // Close mobile sidebar on resize to desktop
        if (window.innerWidth >= 1024) {
          closeMobileSidebar();
        }
      }, 250);
    });
  }

  /**
   * Initialize sidebar accessibility features
   */
  function initAccessibility() {
    // Add ARIA attributes
    if (elements.desktopSidebar) {
      elements.desktopSidebar.setAttribute('aria-label', 'Main navigation');
      elements.desktopSidebar.setAttribute('role', 'navigation');
    }

    if (elements.mobileSidebar) {
      elements.mobileSidebar.setAttribute('aria-label', 'Mobile navigation');
      elements.mobileSidebar.setAttribute('role', 'navigation');
    }

    if (elements.sidebarCollapseToggle) {
      elements.sidebarCollapseToggle.setAttribute(
        'aria-label',
        'Toggle sidebar'
      );
      elements.sidebarCollapseToggle.setAttribute('aria-expanded', 'true');
    }

    // Update aria-expanded when sidebar is toggled
    window.addEventListener('sidebarToggle', (e) => {
      if (elements.sidebarCollapseToggle) {
        elements.sidebarCollapseToggle.setAttribute(
          'aria-expanded',
          !e.detail.isCollapsed
        );
      }
    });
  }

  /**
   * Add smooth scrolling for sidebar navigation
   */
  function initSmoothScrolling() {
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach((link) => {
      link.addEventListener('click', (e) => {
        // Only prevent default for anchor links
        if (link.getAttribute('href').startsWith('#')) {
          e.preventDefault();
          const target = document.querySelector(link.getAttribute('href'));
          if (target) {
            target.scrollIntoView({
              behavior: 'smooth',
              block: 'start',
            });
          }
        }
      });
    });
  }

  /**
   * Initialize all sidebar functionality
   */
  function init() {
    // Check if DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
      return;
    }

    try {
      initDesktopSidebar();
      initMobileSidebar();
      initKeyboardShortcuts();
      initResizeHandler();
      initAccessibility();
      initSmoothScrolling();

      console.log('Sidebar initialized successfully');
    } catch (error) {
      console.error('Error initializing sidebar:', error);
    }
  }

  /**
   * Public API
   */
  window.SidebarManager = {
    toggle: toggleSidebarCollapse,
    collapse: () => {
      if (!isCollapsed) toggleSidebarCollapse();
    },
    expand: () => {
      if (isCollapsed) toggleSidebarCollapse();
    },
    isCollapsed: () => isCollapsed,
    closeMobile: closeMobileSidebar,
  };

  // Initialize when script loads
  init();
})();
