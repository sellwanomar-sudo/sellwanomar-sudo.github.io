// Footer year
document.querySelectorAll('[data-year]').forEach(el => el.textContent = new Date().getFullYear());

// Mobile menu
const toggle = document.querySelector('.menu-toggle');
const links = document.getElementById('nav-links');
if (toggle && links) {
  toggle.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
  });
}

// Dropdowns: click or Enter/Space opens, Escape closes, focus leaving closes
const menus = document.querySelectorAll('.menu-btn');
const closeMenu = btn => {
  btn.setAttribute('aria-expanded', 'false');
  document.getElementById(btn.getAttribute('aria-controls')).classList.remove('open');
};
menus.forEach(btn => {
  const panel = document.getElementById(btn.getAttribute('aria-controls'));
  btn.addEventListener('click', () => {
    const open = btn.getAttribute('aria-expanded') !== 'true';
    menus.forEach(b => b !== btn && closeMenu(b));
    btn.setAttribute('aria-expanded', open);
    panel.classList.toggle('open', open);
  });
  btn.parentElement.addEventListener('keydown', e => {
    if (e.key === 'Escape' && btn.getAttribute('aria-expanded') === 'true') {
      closeMenu(btn);
      btn.focus();
    }
  });
  btn.parentElement.addEventListener('focusout', e => {
    if (!btn.parentElement.contains(e.relatedTarget)) closeMenu(btn);
  });
});
document.addEventListener('click', e => {
  menus.forEach(btn => { if (!btn.parentElement.contains(e.target)) closeMenu(btn); });
});

// Work filters: one choice per group, cards must match every group
const groups = document.querySelectorAll('.filters[data-group]');
const status = document.querySelector('.filter-status');
groups.forEach(group => group.addEventListener('click', e => {
  const btn = e.target.closest('.filter');
  if (!btn) return;
  group.querySelectorAll('.filter').forEach(b => b.setAttribute('aria-pressed', b === btn));
  const active = {};
  groups.forEach(g => active[g.dataset.group] = g.querySelector('[aria-pressed="true"]').dataset.filter);
  let shown = 0;
  document.querySelectorAll('.workgrid .work').forEach(card => {
    const ok = Object.entries(active).every(([k, v]) => v === 'all' || card.dataset[k].split(' ').includes(v));
    card.hidden = !ok;
    if (ok) shown++;
  });
  if (status) status.textContent = shown === 1 ? 'Showing 1 case study' : `Showing ${shown} case studies`;
}));

// Contact form (sent through Web3Forms)
const form = document.getElementById('contact-form');
if (form) {
  const msg = form.querySelector('.form-status');
  form.addEventListener('submit', async e => {
    e.preventDefault();
    if (form.access_key.value.includes('YOUR_')) {
      msg.className = 'form-status err';
      msg.textContent = 'The form is not connected yet. Please email team@contentauthoritylab.com instead.';
      return;
    }
    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    msg.className = 'form-status';
    msg.textContent = 'Sending...';
    try {
      const res = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(Object.fromEntries(new FormData(form)))
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.message);
      form.reset();
      msg.className = 'form-status ok';
      msg.textContent = 'Thank you. Your message is in, and we reply within 1 to 2 business days.';
    } catch (err) {
      msg.className = 'form-status err';
      msg.textContent = 'Something went wrong. Please try again or email team@contentauthoritylab.com.';
    } finally {
      button.disabled = false;
    }
  });
}
