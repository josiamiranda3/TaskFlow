
import { Injectable, inject } from '@angular/core';
import {
  HttpClient,
  HttpHeaders,
} from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import { environment } from '../../environments/environment';
import { AuthService } from './auth';

export type TaskStatus =
  | 'pending'
  | 'in_progress'
  | 'completed';

export type TaskPriority =
  | 'low'
  | 'medium'
  | 'high';

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string | null;
}

export type TaskUpdate = Partial<TaskCreate>;

@Injectable({
  providedIn: 'root',
})
export class TaskService {
  private readonly http = inject(HttpClient);
  private readonly authService = inject(AuthService);

  private readonly apiUrl = `${environment.apiUrl}/tasks`;

  private async getAuthHeaders(): Promise<HttpHeaders> {
    const token = await this.authService.getAccessToken();

    if (!token) {
      throw new Error(
        'Sessão expirada. Entre novamente na sua conta.',
      );
    }

    return new HttpHeaders({
      Authorization: `Bearer ${token}`,
    });
  }

  async listTasks(): Promise<Task[]> {
    const headers = await this.getAuthHeaders();

    return firstValueFrom(
      this.http.get<Task[]>(this.apiUrl, { headers }),
    );
  }

  async createTask(data: TaskCreate): Promise<Task> {
    const headers = await this.getAuthHeaders();

    return firstValueFrom(
      this.http.post<Task>(this.apiUrl, data, { headers }),
    );
  }

  async updateTask(
    taskId: string,
    data: TaskUpdate,
  ): Promise<Task> {
    const headers = await this.getAuthHeaders();

    return firstValueFrom(
      this.http.patch<Task>(
        `${this.apiUrl}/${taskId}`,
        data,
        { headers },
      ),
    );
  }

  async deleteTask(taskId: string): Promise<void> {
    const headers = await this.getAuthHeaders();

    await firstValueFrom(
      this.http.delete<void>(
        `${this.apiUrl}/${taskId}`,
        { headers },
      ),
    );
  }
}