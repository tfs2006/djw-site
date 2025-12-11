
// Smooth scroll for same-page anchors
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const id = a.getAttribute('href').slice(1);
    const el = document.getElementById(id);
    if(el){
      e.preventDefault();
      el.scrollIntoView({behavior:'smooth', block:'start'});
    }
  });
});

// Simple click tracking for affiliate links
window.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('a[data-affiliate]').forEach(a => {
    a.addEventListener('click', () => {
      const label = a.dataset.label || a.textContent.trim();
      if(window.gtag){
        gtag('event', 'affiliate_click', {
          event_category: 'engagement',
          event_label: label
        });
      }
    });
  });
});

// Subtle mouse follow glow effect
document.addEventListener('DOMContentLoaded', () => {
  const glow = document.createElement('div');
  glow.className = 'mouse-glow';
  glow.style.cssText = `
    position: fixed;
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 212, 170, 0.06) 0%, transparent 70%);
    pointer-events: none;
    z-index: -1;
    transform: translate(-50%, -50%);
    transition: opacity 0.3s ease;
    opacity: 0;
  `;
  document.body.appendChild(glow);

  let mouseX = 0, mouseY = 0;
  let glowX = 0, glowY = 0;

  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    glow.style.opacity = '1';
  });

  document.addEventListener('mouseleave', () => {
    glow.style.opacity = '0';
  });

  // Smooth animation loop
  function animateGlow() {
    glowX += (mouseX - glowX) * 0.1;
    glowY += (mouseY - glowY) * 0.1;
    glow.style.left = glowX + 'px';
    glow.style.top = glowY + 'px';
    requestAnimationFrame(animateGlow);
  }
  animateGlow();
});

// Intersection Observer for scroll-triggered animations
document.addEventListener('DOMContentLoaded', () => {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);

  // Observe all cards
  document.querySelectorAll('.card').forEach(card => {
    observer.observe(card);
  });
});

// Magnetic hover effect for buttons
document.addEventListener('DOMContentLoaded', () => {
  const magneticElements = document.querySelectorAll('.cta-btn, .email-btn');
  
  magneticElements.forEach(el => {
    el.addEventListener('mousemove', (e) => {
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      
      el.style.transform = `translate(${x * 0.1}px, ${y * 0.1}px)`;
    });
    
    el.addEventListener('mouseleave', () => {
      el.style.transform = 'translate(0, 0)';
    });
  });
});

// Animate stats on scroll
document.addEventListener('DOMContentLoaded', () => {
  const statNumbers = document.querySelectorAll('.stat-number');
  let hasAnimated = false;
  
  const animateStats = () => {
    if (hasAnimated) return;
    
    const heroStats = document.querySelector('.hero-stats');
    if (!heroStats) return;
    
    const rect = heroStats.getBoundingClientRect();
    if (rect.top < window.innerHeight && rect.bottom > 0) {
      hasAnimated = true;
      
      statNumbers.forEach(stat => {
        const text = stat.textContent;
        const match = text.match(/(\d+)/);
        if (match) {
          const finalNum = parseInt(match[0]);
          const suffix = text.replace(/[\d,]/g, '');
          let current = 0;
          const duration = 1500;
          const startTime = performance.now();
          
          const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            current = Math.floor(finalNum * easeProgress);
            stat.textContent = current.toLocaleString() + suffix;
            
            if (progress < 1) {
              requestAnimationFrame(animate);
            } else {
              stat.textContent = text;
            }
          };
          requestAnimationFrame(animate);
        }
      });
    }
  };
  
  window.addEventListener('scroll', animateStats);
  animateStats(); // Check on load
});
