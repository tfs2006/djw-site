
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
