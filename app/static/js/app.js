/* GPAS — small enhancements; the app is fully usable without JS */
(function () {
  'use strict';

  // Auto-dismiss flash messages after 6s
  document.querySelectorAll('.alert-dismissible').forEach(function (el) {
    setTimeout(function () {
      try { bootstrap.Alert.getOrCreateInstance(el).close(); } catch (e) {}
    }, 6000);
  });

  // Confirm destructive actions
  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!confirm(form.getAttribute('data-confirm'))) e.preventDefault();
    });
  });
})();
