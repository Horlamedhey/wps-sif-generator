<script>
  import { injectAnalytics } from '@vercel/analytics/sveltekit'
  import '../app.css';

  injectAnalytics();
</script>

<svelte:head>
  <script>
    (function () {
      try {
        var root = document.documentElement;
        var savedTheme = localStorage.getItem('wps-theme');
        var theme = savedTheme === 'dark' || savedTheme === 'light'
          ? savedTheme
          : (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        root.classList.remove('theme-light', 'theme-dark');
        root.classList.add(theme === 'dark' ? 'theme-dark' : 'theme-light');
        root.dataset.theme = theme;

        var savedLanguage = localStorage.getItem('wps-language');
        var lang = savedLanguage === 'ar' || savedLanguage === 'en'
          ? savedLanguage
          : ((navigator.language || '').toLowerCase().indexOf('ar') === 0 ? 'ar' : 'en');
        root.lang = lang;
        root.dir = lang === 'ar' ? 'rtl' : 'ltr';
      } catch (e) {
        // no-op
      }
    })();
  </script>
</svelte:head>

<slot />
