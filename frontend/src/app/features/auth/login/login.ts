
import { ChangeDetectorRef, Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import { AuthService } from '../../../core/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  email = '';
  password = '';
  loading = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    private readonly authService: AuthService,
    private readonly router: Router,
    private readonly cdr: ChangeDetectorRef,
  ) {}

  async onSubmit(): Promise<void> {
    if (this.loading) {
      return;
    }

    this.errorMessage = '';
    this.successMessage = '';

    const email = this.email.trim();

    if (!email || !this.password) {
      this.errorMessage = 'Preencha o e-mail e a senha.';
      return;
    }

    this.loading = true;
    this.cdr.markForCheck();

    try {
      const { error } = await this.authService.signIn(
        email,
        this.password,
      );

      if (error) {
        this.errorMessage =
          'Não foi possível entrar. Confira o e-mail e a senha.';
        return;
      }

      this.password = '';
      await this.router.navigate(['/dashboard']);
    } catch (error) {
      console.error('Erro ao realizar login:', error);

      this.errorMessage =
        'Não foi possível conectar ao serviço de autenticação.';
    } finally {
      this.loading = false;
      this.cdr.markForCheck();
    }
  }
}