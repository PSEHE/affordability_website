/**
 * Content Loader for Energy Affordability Website
 * 
 * This module handles loading and rendering Markdown content into HTML pages.
 * It supports:
 * - Markdown parsing with images
 * - Custom image syntax for figures with captions
 * - Section navigation generation
 * - Dynamic content loading
 * 
 * USAGE:
 * 1. Include this script in your HTML page
 * 2. Add a container with id="markdown-content" or data-content-source="path/to/file.md"
 * 3. Call ContentLoader.init() on page load
 * 
 * MARKDOWN EXTENSIONS:
 * - Standard Markdown syntax
 * - ![alt text](image.png "Optional caption") - Image with caption
 * - ![alt text](image.png){.class-name} - Image with CSS class
 * - :::note / :::warning / :::tip - Callout boxes
 */

const ContentLoader = {
    // Configuration
    config: {
        contentBasePath: '../content/',
        imageBasePath: '../assets/',
        defaultContentId: 'markdown-content',
        generateTOC: true,
        tocContainerId: 'table-of-contents'
    },

    /**
     * Initialize the content loader
     * @param {Object} options - Override default configuration
     */
    init: function(options = {}) {
        this.config = { ...this.config, ...options };
        
        // Find all content containers
        const containers = document.querySelectorAll('[data-content-source]');
        
        if (containers.length > 0) {
            containers.forEach(container => {
                const source = container.dataset.contentSource;
                this.loadContent(source, container);
            });

            // Retry logic: sometimes assets or other scripts block execution.
            // If a container wasn't populated (no dataset.lastRendered), try again a few times.
            const retryContainers = Array.from(containers);
            let attempts = 0;
            const maxAttempts = 3;
            const retryInterval = 1000; // ms

            const retryTimer = setInterval(() => {
                attempts += 1;
                retryContainers.forEach(container => {
                    // If dataset.lastRendered is not present, re-run load
                    if (!container.dataset || !container.dataset.lastRendered) {
                        const source = container.dataset.contentSource;
                        console.debug(`ContentLoader: retrying load for ${source}, attempt ${attempts}`);
                        this.loadContent(source, container);
                    }
                });
                if (attempts >= maxAttempts) clearInterval(retryTimer);
            }, retryInterval);
        } else {
            // Try default container
            const defaultContainer = document.getElementById(this.config.defaultContentId);
            if (defaultContainer && defaultContainer.dataset.contentSource) {
                this.loadContent(defaultContainer.dataset.contentSource, defaultContainer);
            }
        }
    },

    /**
     * Load markdown content from a file
     * @param {string} filePath - Path to the markdown file
     * @param {HTMLElement} container - Container element to render into
     */
    loadContent: async function(filePath, container) {
        // Check if we're running on file:// protocol (local file system)
        // In this case, fetch won't work, so we keep the fallback HTML content
        if (window.location.protocol === 'file:') {
            console.log('Running on file:// protocol - using fallback HTML content');
            // Remove loading indicator if any, keep existing content
            container.classList.add('markdown-content');
            this.initializeInteractiveElements(container);
            return;
        }
        
        try {
            // Show loading state - but save fallback content first
            const fallbackContent = container.innerHTML;
            container.innerHTML = '<div class="loading"><div class="loading-spinner"></div></div>';
            
            // Construct full path
            const fullPath = filePath.startsWith('http') ? filePath : this.config.contentBasePath + filePath;
            console.debug(`ContentLoader: fetching markdown from ${fullPath}`);

            const response = await fetch(fullPath, { cache: 'no-store' });
            console.debug(`ContentLoader: received response for ${fullPath} -> ${response.status}`);

            if (!response.ok) {
                throw new Error(`Failed to load content: ${response.status}`);
            }
            
            const markdown = await response.text();
            console.debug(`ContentLoader: fetched markdown snippet: ${markdown.slice(0,200).replace(/\n/g, '\\n')}`);
            const html = this.parseMarkdown(markdown);
            console.debug(`ContentLoader: rendered HTML snippet: ${html.slice(0,200).replace(/\n/g, '\\n')}`);

            // Expose short debug snippets on the container for inspection in Elements panel
            try {
                container.dataset.lastMarkdown = markdown.slice(0,800);
                container.dataset.lastRendered = html.slice(0,800);
            } catch (e) {
                // dataset may throw if too long in some browsers; ignore
                console.debug('ContentLoader: could not set dataset debug info', e);
            }

            container.innerHTML = html;
            container.classList.add('markdown-content');
            
            // Generate table of contents if enabled
            if (this.config.generateTOC) {
                this.generateTableOfContents(container);
            }
            
            // Initialize any interactive elements
            this.initializeInteractiveElements(container);
            
            // Trigger fade-in animations
            this.triggerAnimations(container);
            
        } catch (error) {
            console.warn('Content loading notice:', error.message);
            // Restore fallback content if fetch fails
            container.innerHTML = fallbackContent;
            container.classList.add('markdown-content');
            // Initialize interactive elements on fallback content
            this.initializeInteractiveElements(container);
        }
    },

    /**
     * Parse Markdown to HTML
     * @param {string} markdown - Markdown content
     * @returns {string} - HTML string
     */
    parseMarkdown: function(markdown) {
        let html = markdown;
        
        // Escape HTML entities (but preserve our custom syntax)
        html = html.replace(/&/g, '&amp;')
                   .replace(/</g, '&lt;')
                   .replace(/>/g, '&gt;');
        
        // Process callout boxes first (:::note, :::warning, :::tip)
        html = this.parseCallouts(html);
        
        // Headers
        html = html.replace(/^######\s+(.+)$/gm, '<h6>$1</h6>');
        html = html.replace(/^#####\s+(.+)$/gm, '<h5>$1</h5>');
        html = html.replace(/^####\s+(.+)$/gm, '<h4>$1</h4>');
        html = html.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
        html = html.replace(/^##\s+(.+)$/gm, '<h2 id="$1">$1</h2>');
        html = html.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');
        
        // Generate proper IDs for headers
        html = html.replace(/<h2 id="(.+?)">(.+?)<\/h2>/g, (match, text, content) => {
            const id = this.slugify(content);
            return `<h2 id="${id}">${content}</h2>`;
        });
        
        // Bold and Italic
        html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
        html = html.replace(/___(.+?)___/g, '<strong><em>$1</em></strong>');
        html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');
        html = html.replace(/_(.+?)_/g, '<em>$1</em>');
        
        // Images with captions: ![alt](src "caption")
        html = html.replace(/!\[([^\]]*)\]\(([^)"]+)\s+"([^"]+)"\)/g, (match, alt, src, caption) => {
            const fullSrc = this.resolveImagePath(src);
            return `<figure class="figure">
                <img src="${fullSrc}" alt="${alt}" loading="lazy">
                <figcaption class="figure-caption">${caption}</figcaption>
            </figure>`;
        });
        
        // Images with class: ![alt](src){.class}
        html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)\{\.([^}]+)\}/g, (match, alt, src, className) => {
            const fullSrc = this.resolveImagePath(src);
            return `<img src="${fullSrc}" alt="${alt}" class="${className}" loading="lazy">`;
        });
        
        // Standard images
        html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, src) => {
            const fullSrc = this.resolveImagePath(src);
            return `<img src="${fullSrc}" alt="${alt}" loading="lazy">`;
        });
        
        // Links
        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
        
        // Inline code
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Code blocks
        html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
            const langClass = lang ? ` class="language-${lang}"` : '';
            return `<pre${langClass}><code>${code.trim()}</code></pre>`;
        });
        
        // Blockquotes
        html = html.replace(/^&gt;\s+(.+)$/gm, '<blockquote>$1</blockquote>');
        // Merge consecutive blockquotes
        html = html.replace(/<\/blockquote>\n<blockquote>/g, '\n');
        
        // Horizontal rules
        html = html.replace(/^---+$/gm, '<hr>');
        html = html.replace(/^\*\*\*+$/gm, '<hr>');
        
        // Unordered lists
        html = this.parseLists(html);
        
        // Paragraphs (must be done last)
        html = this.parseParagraphs(html);
        
        return html;
    },

    /**
     * Parse callout boxes (:::note, :::warning, etc.)
     */
    parseCallouts: function(markdown) {
        const calloutTypes = ['note', 'warning', 'tip', 'info', 'important'];
        let result = markdown;
        
        calloutTypes.forEach(type => {
            const regex = new RegExp(`:::${type}\\n([\\s\\S]*?):::`, 'gi');
            result = result.replace(regex, (match, content) => {
                return `<div class="info-box ${type}">${content.trim()}</div>`;
            });
        });
        
        return result;
    },

    /**
     * Parse unordered and ordered lists
     */
    parseLists: function(html) {
        // Unordered lists
        let lines = html.split('\n');
        let inList = false;
        let listType = '';
        let result = [];
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const ulMatch = line.match(/^[\-\*]\s+(.+)$/);
            const olMatch = line.match(/^\d+\.\s+(.+)$/);
            
            if (ulMatch) {
                if (!inList || listType !== 'ul') {
                    if (inList) result.push(`</${listType}>`);
                    result.push('<ul>');
                    inList = true;
                    listType = 'ul';
                }
                result.push(`<li>${ulMatch[1]}</li>`);
            } else if (olMatch) {
                if (!inList || listType !== 'ol') {
                    if (inList) result.push(`</${listType}>`);
                    result.push('<ol>');
                    inList = true;
                    listType = 'ol';
                }
                result.push(`<li>${olMatch[1]}</li>`);
            } else {
                if (inList) {
                    result.push(`</${listType}>`);
                    inList = false;
                    listType = '';
                }
                result.push(line);
            }
        }
        
        if (inList) {
            result.push(`</${listType}>`);
        }
        
        return result.join('\n');
    },

    /**
     * Wrap text in paragraph tags
     */
    parseParagraphs: function(html) {
        const blocks = html.split(/\n\n+/);
        
        return blocks.map(block => {
            block = block.trim();
            
            // Don't wrap if already a block element
            if (block.match(/^<(h[1-6]|ul|ol|li|blockquote|pre|div|figure|hr|table)/i)) {
                return block;
            }
            
            // Don't wrap empty blocks
            if (!block) return '';
            
            // Wrap in paragraph
            return `<p>${block.replace(/\n/g, '<br>')}</p>`;
        }).join('\n\n');
    },

    /**
     * Resolve image path
     */
    resolveImagePath: function(src) {
        // If it's already an absolute URL or data URI, return as-is
        if (src.startsWith('http') || src.startsWith('data:') || src.startsWith('/')) {
            return src;
        }
        // Otherwise, prepend the image base path
        return this.config.imageBasePath + src;
    },

    /**
     * Create URL-safe slug from text
     */
    slugify: function(text) {
        return text
            .toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim();
    },

    /**
     * Generate table of contents from headers
     */
    generateTableOfContents: function(container) {
        const tocContainer = document.getElementById(this.config.tocContainerId);
        if (!tocContainer) return;
        
        const headers = container.querySelectorAll('h2, h3, h4, h5');
        if (headers.length === 0) return;
        
        // Build TOC HTML with proper nesting classes
        let tocHTML = '<nav class="toc">';
        tocHTML += '<div class="toc-progress"><div class="toc-progress-bar"></div></div>';
        tocHTML += '<h4>On This Page</h4><ul class="toc-list">';
        
        headers.forEach(header => {
            const level = header.tagName.toLowerCase();
            const id = header.id || this.slugify(header.textContent);
            header.id = id;
            
            // Add scroll-margin-top for fixed header offset
            header.style.scrollMarginTop = 'calc(var(--navbar-height, 72px) + 1.5rem)';
            
            tocHTML += `<li class="toc-${level}"><a href="#${id}" data-target="${id}">${header.textContent}</a></li>`;
        });
        
        tocHTML += '</ul></nav>';
        tocContainer.innerHTML = tocHTML;
        
        // Initialize scroll spy
        this.initScrollSpy(container, tocContainer, headers);
    },
    
    /**
     * Initialize scroll spy for TOC
     */
    initScrollSpy: function(contentContainer, tocContainer, headers) {
        const tocLinks = tocContainer.querySelectorAll('.toc-list a');
        const progressBar = tocContainer.querySelector('.toc-progress-bar');
        
        // Update active link on scroll
        const updateActiveLink = () => {
            const scrollPos = window.scrollY + 120; // Offset for header
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            
            // Update progress bar
            if (progressBar) {
                const scrollPercent = (window.scrollY / docHeight) * 100;
                progressBar.style.width = `${Math.min(scrollPercent, 100)}%`;
            }
            
            // Find current section
            let currentSection = null;
            headers.forEach(header => {
                if (header.offsetTop <= scrollPos) {
                    currentSection = header.id;
                }
            });
            
            // Update active class
            tocLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('data-target') === currentSection) {
                    link.classList.add('active');
                    
                    // Scroll TOC to show active item
                    const tocList = tocContainer.querySelector('.toc-list');
                    if (tocList) {
                        const linkRect = link.getBoundingClientRect();
                        const listRect = tocList.getBoundingClientRect();
                        if (linkRect.top < listRect.top || linkRect.bottom > listRect.bottom) {
                            link.scrollIntoView({ block: 'center', behavior: 'smooth' });
                        }
                    }
                }
            });
        };
        
        // Throttled scroll handler
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    updateActiveLink();
                    ticking = false;
                });
                ticking = true;
            }
        });
        
        // Smooth scroll on TOC link click
        tocLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('data-target');
                const target = document.getElementById(targetId);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                    // Update URL without scrolling
                    history.pushState(null, null, `#${targetId}`);
                }
            });
        });
        
        // Initial update
        updateActiveLink();
    },

    /**
     * Initialize interactive elements (carousels, etc.)
     */
    initializeInteractiveElements: function(container) {
        // Initialize any image galleries
        const galleries = container.querySelectorAll('.image-gallery');
        galleries.forEach(gallery => this.initGallery(gallery));
        
        // Add click-to-zoom for images
        const images = container.querySelectorAll('img:not(.no-zoom)');
        images.forEach(img => {
            img.style.cursor = 'pointer';
            img.addEventListener('click', () => this.openLightbox(img));
        });
    },

    /**
     * Initialize image gallery
     */
    initGallery: function(gallery) {
        const images = gallery.querySelectorAll('img');
        if (images.length <= 1) return;
        
        let currentIndex = 0;
        
        // Create navigation
        const nav = document.createElement('div');
        nav.className = 'gallery-nav';
        nav.innerHTML = `
            <button class="gallery-prev">←</button>
            <span class="gallery-counter">${currentIndex + 1} / ${images.length}</span>
            <button class="gallery-next">→</button>
        `;
        gallery.appendChild(nav);
        
        // Show first image, hide others
        images.forEach((img, i) => {
            img.style.display = i === 0 ? 'block' : 'none';
        });
        
        // Navigation handlers
        nav.querySelector('.gallery-prev').addEventListener('click', () => {
            images[currentIndex].style.display = 'none';
            currentIndex = (currentIndex - 1 + images.length) % images.length;
            images[currentIndex].style.display = 'block';
            nav.querySelector('.gallery-counter').textContent = `${currentIndex + 1} / ${images.length}`;
        });
        
        nav.querySelector('.gallery-next').addEventListener('click', () => {
            images[currentIndex].style.display = 'none';
            currentIndex = (currentIndex + 1) % images.length;
            images[currentIndex].style.display = 'block';
            nav.querySelector('.gallery-counter').textContent = `${currentIndex + 1} / ${images.length}`;
        });
    },

    /**
     * Open image in lightbox
     */
    openLightbox: function(img) {
        const lightbox = document.createElement('div');
        lightbox.className = 'lightbox';
        lightbox.innerHTML = `
            <div class="lightbox-backdrop"></div>
            <div class="lightbox-content">
                <img src="${img.src}" alt="${img.alt}">
                <button class="lightbox-close">&times;</button>
            </div>
        `;
        document.body.appendChild(lightbox);
        document.body.style.overflow = 'hidden';
        
        // Close handlers
        const close = () => {
            lightbox.remove();
            document.body.style.overflow = '';
        };
        
        lightbox.querySelector('.lightbox-backdrop').addEventListener('click', close);
        lightbox.querySelector('.lightbox-close').addEventListener('click', close);
        document.addEventListener('keydown', function escHandler(e) {
            if (e.key === 'Escape') {
                close();
                document.removeEventListener('keydown', escHandler);
            }
        });
    },

    /**
     * Trigger fade-in animations for content
     */
    triggerAnimations: function(container) {
        const elements = container.querySelectorAll('.fade-in');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.1 });
        
        elements.forEach(el => observer.observe(el));
    }
};

// Lightbox styles (injected dynamically)
const lightboxStyles = document.createElement('style');
lightboxStyles.textContent = `
    .lightbox {
        position: fixed;
        inset: 0;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .lightbox-backdrop {
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.9);
    }
    .lightbox-content {
        position: relative;
        max-width: 90vw;
        max-height: 90vh;
    }
    .lightbox-content img {
        max-width: 100%;
        max-height: 90vh;
        object-fit: contain;
        border-radius: 8px;
    }
    .lightbox-close {
        position: absolute;
        top: -40px;
        right: 0;
        background: none;
        border: none;
        color: white;
        font-size: 32px;
        cursor: pointer;
        padding: 8px;
    }
    .lightbox-close:hover {
        color: #fb923c;
    }
    
    /* Table of Contents */
    .toc {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin-bottom: 2rem;
    }
    .toc h4 {
        margin: 0 0 0.75rem 0;
        color: #275258;
    }
    .toc ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .toc li {
        margin-bottom: 0.5rem;
    }
    .toc li.toc-sub {
        padding-left: 1rem;
    }
    .toc a {
        color: #4b5563;
        text-decoration: none;
        font-size: 0.9375rem;
    }
    .toc a:hover {
        color: #fb923c;
    }
    
    /* Gallery navigation */
    .gallery-nav {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin-top: 1rem;
    }
    .gallery-nav button {
        background: #275258;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
    }
    .gallery-nav button:hover {
        background: #fb923c;
    }
    .gallery-counter {
        color: #6b7280;
        font-size: 0.875rem;
    }
`;
document.head.appendChild(lightboxStyles);

// Auto-initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    ContentLoader.init();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ContentLoader;
}
