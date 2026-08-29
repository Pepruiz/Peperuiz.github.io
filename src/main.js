// import './style.css' // CSS Imported in HTML Head for performance


// Sticky Navbar Logic
const navbar = document.getElementById('navbar');

window.addEventListener('scroll', () => {
  if (window.scrollY > 50) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
});

// Smooth Scroll for anchor links (Polyfill-like behavior/Enforcement)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth'
      });
    }
  });
});

// Mobile Navbar Toggle Logic
const mobileToggle = document.getElementById('mobileMenuToggle');

if (mobileToggle && navbar) {
  mobileToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = navbar.classList.toggle('nav-open');
    mobileToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  // Close menu when clicking on any nav link
  document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', () => {
      navbar.classList.remove('nav-open');
      mobileToggle.setAttribute('aria-expanded', 'false');
    });
  });

  // Close menu when clicking outside
  document.addEventListener('click', (e) => {
    if (!navbar.contains(e.target)) {
      navbar.classList.remove('nav-open');
      mobileToggle.setAttribute('aria-expanded', 'false');
    }
  });
}

// Reveal on Scroll
const revealElements = document.querySelectorAll('.reveal');
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('active');
    }
  });
}, { threshold: 0.1 });

revealElements.forEach(el => revealObserver.observe(el));

// Contact Form AJAX Submission with Timeout & Dismissible Alert
const contactForm = document.querySelector('.contact-form');
const formStatus = document.getElementById('formStatus');

if (contactForm && formStatus) {
  // Clear alert when user starts editing fields
  contactForm.querySelectorAll('input, textarea').forEach(field => {
    field.addEventListener('input', () => {
      formStatus.style.display = 'none';
    });
  });

  contactForm.addEventListener('submit', async function (e) {
    e.preventDefault();

    const submitBtn = contactForm.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;

    // Loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Enviando mensaje...';
    formStatus.style.display = 'none';

    const formData = new FormData(contactForm);
    const data = Object.fromEntries(formData.entries());

    // 10-second timeout controller
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    try {
      const response = await fetch('https://formsubmit.co/ajax/ingenieria@rcestructuras.es', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(data),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        formStatus.style.display = 'block';
        formStatus.style.backgroundColor = '#ecfdf5';
        formStatus.style.color = '#065f46';
        formStatus.style.border = '1px solid #a7f3d0';
        formStatus.innerHTML = `
          <button type="button" class="status-close-btn" onclick="this.parentElement.style.display='none'" aria-label="Cerrar">&times;</button>
          ✓ <strong>¡Mensaje enviado con éxito!</strong> Nos pondremos en contacto contigo a la mayor brevedad.
        `;
        contactForm.reset();
      } else {
        throw new Error('Respuesta no válida del servidor');
      }
    } catch (error) {
      clearTimeout(timeoutId);
      formStatus.style.display = 'block';
      formStatus.style.backgroundColor = '#fef2f2';
      formStatus.style.color = '#991b1b';
      formStatus.style.border = '1px solid #fecaca';
      formStatus.innerHTML = `
        <button type="button" class="status-close-btn" onclick="this.parentElement.style.display='none'" aria-label="Cerrar">&times;</button>
        <strong>No se ha podido enviar el mensaje automáticamente.</strong> Por favor, inténtalo de nuevo o escríbenos directamente a <a href="mailto:ingenieria@rcestructuras.es" style="text-decoration:underline; font-weight:600; color:inherit;">ingenieria@rcestructuras.es</a>.
      `;
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnText;
    }
  });
}

console.log('Portfolio initialized with reveal effects, mobile menu and contact handler.');

