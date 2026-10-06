// Fit only the gallery viewport. The standalone iframe keeps its native canvas.
(() => {
  const previews = [...document.querySelectorAll('.preview')];
  function fit(preview) {
    const width = Number(preview.dataset.width);
    const height = Number(preview.dataset.height);
    const scale = Math.min(1, preview.clientWidth / width, 440 / height);
    const iframe = preview.querySelector('iframe');
    preview.style.height = `${height * scale}px`;
    iframe.style.transform = `translateX(-50%) scale(${scale})`;
  }
  previews.forEach(fit);
  if ('ResizeObserver' in window) {
    const observer = new ResizeObserver(entries => entries.forEach(entry => fit(entry.target)));
    previews.forEach(preview => observer.observe(preview));
  } else {
    window.addEventListener('resize', () => previews.forEach(fit));
  }
})();
