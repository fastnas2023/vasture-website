document.addEventListener('DOMContentLoaded', () => {
  const mainImage = document.querySelector('[data-product-main]');
  const label = document.querySelector('[data-product-colour-label]');
  if (!mainImage) return;

  document.querySelectorAll('[data-product-image]').forEach((control) => {
    control.addEventListener('click', () => {
      const image = control.dataset.productImage;
      if (!image) return;
      mainImage.src = image;
      mainImage.alt = control.dataset.productAlt || control.dataset.productLabel || mainImage.alt;
      const nextLabel = control.dataset.productLabel || control.dataset.productAlt;
      if (label && nextLabel) label.textContent = nextLabel;
      document.querySelectorAll('[data-product-image]').forEach((item) => item.classList.toggle('is-active', item === control));
    });
  });
});
