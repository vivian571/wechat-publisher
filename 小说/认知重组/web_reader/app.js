document.addEventListener('DOMContentLoaded', () => {
    const navList = document.getElementById('nav-list');
    const readerContainer = document.getElementById('reader-container');
    const titleBar = document.getElementById('current-chapter-title');

    if (typeof novelData === 'undefined') {
        readerContainer.innerHTML = '<p style="color: var(--accent-red)">Error: data.js not found. Please run build_web.py</p>';
        return;
    }

    // Initialize Navigation
    novelData.forEach((chapter, index) => {
        const div = document.createElement('div');
        div.className = 'nav-item';
        div.textContent = formatTitle(chapter.title);
        div.onclick = () => loadChapter(index);
        navList.appendChild(div);
    });

    function formatTitle(title) {
        // Clean up title for sidebar
        return title.replace(/\.md$/, '').replace(/^\d{2}_/, '');
    }

    function loadChapter(index) {
        // Update Active State
        document.querySelectorAll('.nav-item').forEach((el, i) => {
            el.classList.toggle('active', i === index);
        });

        const chapter = novelData[index];
        titleBar.textContent = `~/${chapter.title}`;
        
        // Fade out
        readerContainer.classList.remove('loaded');
        
        setTimeout(() => {
            // Render Markdown
            readerContainer.innerHTML = marked.parse(chapter.content);
            
            // Apply Typewriter effect to code blocks
            applyTypewriterEffect();
            
            // Fade in
            readerContainer.classList.add('loaded');
            readerContainer.scrollTop = 0;
        }, 300);
    }

    function applyTypewriterEffect() {
        const preBlocks = readerContainer.querySelectorAll('pre code, p code');
        preBlocks.forEach(block => {
            // Only apply to system logs or traceroutes which start with [ or have >>
            if(block.textContent.includes('[System Log') || block.textContent.includes(']') || block.textContent.includes('//') || block.textContent.includes('Status:')) {
                const originalText = block.textContent;
                block.textContent = '';
                block.classList.add('typewriter-cursor');
                
                let i = 0;
                const speed = 10; // typing speed ms
                
                function typeWriter() {
                    if (i < originalText.length) {
                        block.textContent += originalText.charAt(i);
                        i++;
                        setTimeout(typeWriter, speed);
                    } else {
                        block.classList.remove('typewriter-cursor');
                    }
                }
                
                setTimeout(typeWriter, 300);
            }
        });
    }

    // Load first chapter by default
    if (novelData.length > 0) {
        loadChapter(0);
    }
});
