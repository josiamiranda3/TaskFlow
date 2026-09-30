
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import type { AuthError, Session } from '@supabase/supabase-js';

import { supabase } from './supabase.client';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly sessionSubject =
    new BehaviorSubject<Session | null>(null);

  readonly session$ = this.sessionSubject.asObservable();

  constructor() {
    void this.loadSession();

    supabase.auth.onAuthStateChange((_event, session) => {
      this.sessionSubject.next(session);
    });
  }

  private async loadSession(): Promise<void> {
    const { data, error } = await supabase.auth.getSession();

    if (!error) {
      this.sessionSubject.next(data.session);
    }
  }

  async signIn(
    email: string,
    password: string,
  ): Promise<{ error: AuthError | null }> {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (!error) {
      this.sessionSubject.next(data.session);
    }

    return { error };
  }

  async signOut(): Promise<{ error: AuthError | null }> {
    const { error } = await supabase.auth.signOut();

    if (!error) {
      this.sessionSubject.next(null);
    }

    return { error };
  }

  async getAccessToken(): Promise<string | null> {
    const { data, error } = await supabase.auth.getSession();

    if (error) {
      return null;
    }

    this.sessionSubject.next(data.session);

    return data.session?.access_token ?? null;
  }
}