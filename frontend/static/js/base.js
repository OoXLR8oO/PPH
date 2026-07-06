// base.js
import { ensureAuthenticated, goToLogin, setupLogout } from "/static/js/auth.js";


async function initializeAppShell() {
  const isAuthenticated = await ensureAuthenticated();

  if (!isAuthenticated) {
    goToLogin();
    return;
  }

  setupLogout();
}


initializeAppShell();