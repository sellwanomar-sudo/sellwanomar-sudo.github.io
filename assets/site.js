// Footer year
document.querySelectorAll('[data-year]').forEach(el => el.textContent = new Date().getFullYear());

// Mobile menu
const toggle = document.querySelector('.menu-toggle');
const links = document.querySelector('.links');
if (toggle && links) {
  toggle.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
  });
  links.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    links.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
  }));
}

// Work filters
const filters = document.querySelectorAll('.filter');
filters.forEach(btn => btn.addEventListener('click', () => {
  filters.forEach(b => b.setAttribute('aria-pressed', b === btn));
  const cat = btn.dataset.filter;
  document.querySelectorAll('.work').forEach(card => {
    card.hidden = cat !== 'all' && !card.dataset.cat.split(' ').includes(cat);
  });
}));

// Contact form (sent through Web3Forms, free)
const form = document.getElementById('contact-form');
if (form) {
  const status = form.querySelector('.form-status');
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const key = form.querySelector('[name="access_key"]').value;
    if (key.includes('YOUR_')) {
      status.className = 'form-status err';
      status.textContent = 'The form is not connected yet: add your Web3Forms access key (see README step 3).';
      return;
    }
    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    status.className = 'form-status';
    status.textContent = 'Sending…';
    try {
      const res = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(Object.fromEntries(new FormData(form)))
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.message);
      form.reset();
      status.className = 'form-status ok';
      status.textContent = 'Thank you! Your message has been sent. I usually reply within 1–2 business days.';
    } catch (err) {
      status.className = 'form-status err';
      status.textContent = 'Sorry, something went wrong. Please try again or reach me on LinkedIn.';
    } finally {
      button.disabled = false;
    }
  });
}
