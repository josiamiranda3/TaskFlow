
import {
  ChangeDetectorRef,
  Component,
  OnInit,
  inject,
} from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { AuthService } from '../../../core/auth';
import {
  Task,
  TaskCreate,
  TaskPriority,
  TaskService,
  TaskStatus,
  TaskUpdate,
} from '../../../core/task.service';

interface DashboardTask {
  id: string;
  title: string;
  description: string;
  priority: string;
  status: string;
  dueDate: string;
}

interface DashboardStat {
  label: string;
  value: number;
  icon: string;
  color: string;
}

interface TaskFormData {
  title: string;
  description: string;
  priority: TaskPriority;
  status: TaskStatus;
  dueDate: string;
}


type TaskStatusFilter = 'all' | TaskStatus;
type TaskPriorityFilter = 'all' | TaskPriority;
type TaskSortOption = 'newest' | 'oldest' | 'dueDate';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterLink, FormsModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly taskService = inject(TaskService);
  private readonly router = inject(Router);
  private readonly cdr = inject(ChangeDetectorRef);

  logoutError = '';
  loadingLogout = false;

  loadingTasks = false;
  taskLoadError = '';

  showCreateForm = false;
  loadingCreateTask = false;
  taskCreateError = '';
  taskCreateSuccess = '';

  editingTaskId: string | null = null;
  updatingTask = false;
  taskEditError = '';

  deletingTaskId: string | null = null;
  taskActionError = '';
  taskActionSuccess = '';

  newTask: TaskFormData = this.createEmptyForm();

  editTask: TaskFormData = this.createEmptyForm();

  readonly stats: DashboardStat[] = [
    { label: 'Total de tarefas', value: 0, icon: '▤', color: 'blue' },
    { label: 'Concluídas', value: 0, icon: '✓', color: 'green' },
    { label: 'Em andamento', value: 0, icon: '◷', color: 'orange' },
    { label: 'Pendentes', value: 0, icon: '○', color: 'purple' },
  ];

  tasks: DashboardTask[] = [];

  
searchTerm = '';
statusFilter: TaskStatusFilter = 'all';
priorityFilter: TaskPriorityFilter = 'all';
sortOption: TaskSortOption = 'newest';

get filteredTasks(): DashboardTask[] {
  const search = this.searchTerm.trim().toLocaleLowerCase('pt-BR');

  const filtered = this.tasks.filter((task) => {
    const matchesSearch =
      !search ||
      task.title.toLocaleLowerCase('pt-BR').includes(search) ||
      task.description.toLocaleLowerCase('pt-BR').includes(search);

    const matchesStatus =
      this.statusFilter === 'all' ||
      this.toTaskStatus(task.status) === this.statusFilter;

    const matchesPriority =
      this.priorityFilter === 'all' ||
      this.toTaskPriority(task.priority) === this.priorityFilter;

    return matchesSearch && matchesStatus && matchesPriority;
  });

  return filtered.sort((a, b) => {
    if (this.sortOption === 'dueDate') {
      const dateA = this.parseDueDate(a.dueDate);
      const dateB = this.parseDueDate(b.dueDate);

      return dateA - dateB;
    }

    const indexA = this.tasks.findIndex((task) => task.id === a.id);
    const indexB = this.tasks.findIndex((task) => task.id === b.id);

    return this.sortOption === 'newest'
      ? indexA - indexB
      : indexB - indexA;
  });
}

private parseDueDate(date: string): number {
  if (!date || date === 'Sem prazo' || date === 'Data inválida') {
    return Number.MAX_SAFE_INTEGER;
  }

  const [day, month, year] = date.split('/').map(Number);

  if (!day || !month || !year) {
    return Number.MAX_SAFE_INTEGER;
  }

  return new Date(year, month - 1, day).getTime();
}

clearFilters(): void {
  this.searchTerm = '';
  this.statusFilter = 'all';
  this.priorityFilter = 'all';
  this.sortOption = 'newest';
}

  ngOnInit(): void {
    void this.loadTasks();
  }

  async loadTasks(): Promise<void> {
    this.loadingTasks = true;
    this.taskLoadError = '';
    this.cdr.markForCheck();

    try {
      const result = await this.taskService.listTasks();

      this.tasks = result.map((task) => this.toDashboardTask(task));
      this.updateStats(result);
    } catch (error: unknown) {
      console.error('Erro ao carregar tarefas:', error);

      this.taskLoadError = this.getErrorMessage(
        error,
        'Não foi possível carregar as tarefas.',
      );
    } finally {
      this.loadingTasks = false;
      this.cdr.markForCheck();
    }
  }

  openCreateForm(): void {
    this.taskCreateError = '';
    this.taskCreateSuccess = '';
    this.taskActionError = '';
    this.taskActionSuccess = '';

    this.showCreateForm = !this.showCreateForm;

    if (this.showCreateForm) {
      this.newTask = this.createEmptyForm();
    }

    this.cdr.markForCheck();
  }

  async onCreateTask(): Promise<void> {
    if (this.loadingCreateTask) {
      return;
    }

    this.taskCreateError = '';
    this.taskCreateSuccess = '';

    const title = this.newTask.title.trim();

    if (!title) {
      this.taskCreateError = 'Informe o título da tarefa.';
      this.cdr.markForCheck();
      return;
    }

    if (title.length > 150) {
      this.taskCreateError =
        'O título deve ter no máximo 150 caracteres.';
      this.cdr.markForCheck();
      return;
    }

    this.loadingCreateTask = true;
    this.cdr.markForCheck();

    try {
      const taskData: TaskCreate = {
        title,
        description: this.newTask.description.trim() || null,
        priority: this.newTask.priority,
        status: this.newTask.status,
        due_date: this.toIsoDate(this.newTask.dueDate),
      };

      const createdTask =
        await this.taskService.createTask(taskData);

      this.tasks = [
        this.toDashboardTask(createdTask),
        ...this.tasks.filter((task) => task.id !== createdTask.id),
      ];

      this.updateStatsFromDashboardTasks();

      this.newTask = this.createEmptyForm();
      this.showCreateForm = false;
      this.taskCreateSuccess = 'Tarefa cadastrada com sucesso!';

      this.cdr.markForCheck();

      // Atualiza os dados a partir da API.
      void this.loadTasks();
    } catch (error: unknown) {
      console.error('Erro ao cadastrar tarefa:', error);

      this.taskCreateError = this.getErrorMessage(
        error,
        'Não foi possível cadastrar a tarefa.',
      );
    } finally {
      this.loadingCreateTask = false;
      this.cdr.markForCheck();
    }
  }

  onEditTask(task: DashboardTask): void {
    const priority = this.toTaskPriority(task.priority);
    const status = this.toTaskStatus(task.status);

    this.editingTaskId = task.id;
    this.taskEditError = '';
    this.taskActionError = '';
    this.taskActionSuccess = '';
    this.taskCreateSuccess = '';
    this.showCreateForm = false;

    this.editTask = {
      title: task.title,
      description: task.description,
      priority,
      status,
      dueDate: this.toInputDate(task.dueDate),
    };

    this.cdr.markForCheck();
  }

  onCancelEdit(): void {
    if (this.updatingTask) {
      return;
    }

    this.editingTaskId = null;
    this.taskEditError = '';
    this.editTask = this.createEmptyForm();
    this.cdr.markForCheck();
  }

  async onUpdateTask(): Promise<void> {
    if (this.updatingTask || !this.editingTaskId) {
      return;
    }

    const taskId = this.editingTaskId;
    const title = this.editTask.title.trim();

    this.taskEditError = '';
    this.taskActionError = '';
    this.taskActionSuccess = '';

    if (!title) {
      this.taskEditError = 'Informe o título da tarefa.';
      this.cdr.markForCheck();
      return;
    }

    if (title.length > 150) {
      this.taskEditError =
        'O título deve ter no máximo 150 caracteres.';
      this.cdr.markForCheck();
      return;
    }

    this.updatingTask = true;
    this.cdr.markForCheck();

    try {
      const changes: TaskUpdate = {
        title,
        description: this.editTask.description.trim() || null,
        priority: this.editTask.priority,
        status: this.editTask.status,
        due_date: this.toIsoDate(this.editTask.dueDate),
      };

      const updatedTask = await this.taskService.updateTask(
        taskId,
        changes,
      );

      this.tasks = this.tasks.map((task) =>
        task.id === taskId
          ? this.toDashboardTask(updatedTask)
          : task,
      );

      this.updateStatsFromDashboardTasks();

      this.editingTaskId = null;
      this.editTask = this.createEmptyForm();
      this.taskActionSuccess = 'Tarefa atualizada com sucesso!';

      this.cdr.markForCheck();

      // Confirma a sincronização com o backend.
      void this.loadTasks();
    } catch (error: unknown) {
      console.error('Erro ao atualizar tarefa:', error);

      this.taskEditError = this.getErrorMessage(
        error,
        'Não foi possível atualizar a tarefa.',
      );
    } finally {
      this.updatingTask = false;
      this.cdr.markForCheck();
    }
  }

  async onDeleteTask(task: DashboardTask): Promise<void> {
    if (this.deletingTaskId || this.editingTaskId) {
      return;
    }

    const confirmed = window.confirm(
      `Deseja realmente excluir a tarefa "${task.title}"? Esta ação não pode ser desfeita.`,
    );

    if (!confirmed) {
      return;
    }

    this.deletingTaskId = task.id;
    this.taskActionError = '';
    this.taskActionSuccess = '';
    this.taskCreateSuccess = '';
    this.cdr.markForCheck();

    try {
      await this.taskService.deleteTask(task.id);

      this.tasks = this.tasks.filter(
        (item) => item.id !== task.id,
      );

      this.updateStatsFromDashboardTasks();

      this.taskActionSuccess = 'Tarefa excluída com sucesso!';
      this.cdr.markForCheck();

      void this.loadTasks();
    } catch (error: unknown) {
      console.error('Erro ao excluir tarefa:', error);

      this.taskActionError = this.getErrorMessage(
        error,
        'Não foi possível excluir a tarefa.',
      );
    } finally {
      this.deletingTaskId = null;
      this.cdr.markForCheck();
    }
  }

  private createEmptyForm(): TaskFormData {
    return {
      title: '',
      description: '',
      priority: 'medium',
      status: 'pending',
      dueDate: '',
    };
  }

  private toDashboardTask(task: Task): DashboardTask {
    return {
      id: task.id,
      title: task.title,
      description: task.description ?? '',
      priority: this.formatPriority(task.priority),
      status: this.formatStatus(task.status),
      dueDate: this.formatDueDate(task.due_date),
    };
  }

  private toTaskPriority(priority: string): TaskPriority {
    const values: Record<string, TaskPriority> = {
      Baixa: 'low',
      Média: 'medium',
      Alta: 'high',
      low: 'low',
      medium: 'medium',
      high: 'high',
    };

    return values[priority] ?? 'medium';
  }

  private toTaskStatus(status: string): TaskStatus {
    const values: Record<string, TaskStatus> = {
      Pendente: 'pending',
      'Em andamento': 'in_progress',
      Concluída: 'completed',
      pending: 'pending',
      in_progress: 'in_progress',
      completed: 'completed',
    };

    return values[status] ?? 'pending';
  }

  private updateStats(result: Task[]): void {
    this.stats[0].value = result.length;
    this.stats[1].value = result.filter(
      (task) => task.status === 'completed',
    ).length;
    this.stats[2].value = result.filter(
      (task) => task.status === 'in_progress',
    ).length;
    this.stats[3].value = result.filter(
      (task) => task.status === 'pending',
    ).length;
  }

  private updateStatsFromDashboardTasks(): void {
    this.stats[0].value = this.tasks.length;
    this.stats[1].value = this.tasks.filter(
      (task) => task.status === 'Concluída',
    ).length;
    this.stats[2].value = this.tasks.filter(
      (task) => task.status === 'Em andamento',
    ).length;
    this.stats[3].value = this.tasks.filter(
      (task) => task.status === 'Pendente',
    ).length;
  }

  private toIsoDate(date: string): string | null {
    if (!date) {
      return null;
    }

    const parsed = new Date(`${date}T12:00:00`);

    if (Number.isNaN(parsed.getTime())) {
      return null;
    }

    return parsed.toISOString();
  }

  private toInputDate(date: string): string {
    if (!date || date === 'Sem prazo' || date === 'Data inválida') {
      return '';
    }

    // A data exibida já foi formatada em pt-BR.
    const parts = date.split('/');

    if (parts.length === 3) {
      const [day, month, year] = parts;
      return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    }

    return '';
  }

  private getErrorMessage(
    error: unknown,
    fallback: string,
  ): string {
    if (
      typeof error === 'object' &&
      error !== null &&
      'error' in error
    ) {
      const response = error.error;

      if (
        typeof response === 'object' &&
        response !== null &&
        'detail' in response &&
        typeof response.detail === 'string'
      ) {
        return response.detail;
      }
    }

    if (error instanceof Error) {
      return error.message;
    }

    return fallback;
  }

  private formatPriority(priority: TaskPriority): string {
    const labels: Record<TaskPriority, string> = {
      low: 'Baixa',
      medium: 'Média',
      high: 'Alta',
    };

    return labels[priority];
  }

  private formatStatus(status: TaskStatus): string {
    const labels: Record<TaskStatus, string> = {
      pending: 'Pendente',
      in_progress: 'Em andamento',
      completed: 'Concluída',
    };

    return labels[status];
  }

  private formatDueDate(date: string | null): string {
    if (!date) {
      return 'Sem prazo';
    }

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) {
      return 'Data inválida';
    }

    return new Intl.DateTimeFormat('pt-BR', {
      timeZone: 'UTC',
    }).format(parsedDate);
  }

  async onSignOut(): Promise<void> {
    if (this.loadingLogout) {
      return;
    }

    this.loadingLogout = true;
    this.logoutError = '';
    this.cdr.markForCheck();

    try {
      const { error } = await this.authService.signOut();

      if (error) {
        this.logoutError =
          'Não foi possível sair da conta. Tente novamente.';
        return;
      }

      await this.router.navigate(['/login'], {
        replaceUrl: true,
      });
    } catch {
      this.logoutError =
        'Ocorreu um erro ao encerrar a sessão.';
    } finally {
      this.loadingLogout = false;
      this.cdr.markForCheck();
    }
  }
  
scrollToTasks(event: Event): void {
  event.preventDefault();

  document.getElementById('tarefas')?.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  });
}
}

