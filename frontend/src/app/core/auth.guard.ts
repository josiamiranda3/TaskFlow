
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { AuthService } from './auth';

export const authGuard: CanActivateFn = async () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  try {
    const accessToken = await authService.getAccessToken();

    if (accessToken) {
      return true;
    }
  } catch {
    // Se houver falha na verificação, negar o acesso.
  }

  return router.createUrlTree(['/login']);
};