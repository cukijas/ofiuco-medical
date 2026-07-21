import apiClient from './client';
import type {
  TokenResponse,
  User,
  Client,
  ClientListResponse,
  Equipment,
  EquipmentListResponse,
  OrdenServicio,
  OrdenServicioListResponse,
  Empleado,
  Departamento,
  Attachment,
  AttachmentListResponse,
  PaginationParams,
  Category,
  CategoryListResponse,
  Subcategory,
  SubcategoryListResponse,
  TipoEquipo,
  Marca,
  SubtipoEquipo,
} from '../types';

// Auth
export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post<TokenResponse>('/auth/login', { email, password }).then((r) => r.data),

  register: (email: string, password: string, full_name?: string, role?: string) =>
    apiClient
      .post<User>('/auth/register', { email, password, full_name, role })
      .then((r) => r.data),

  me: () => apiClient.get<User>('/auth/me').then((r) => r.data),

  logout: () => apiClient.post('/auth/logout'),
};

// Clients
export const clientsApi = {
  list: (params: PaginationParams) =>
    apiClient.get<ClientListResponse>('/clientes', { params }).then((r) => r.data),

  get: (id: number) => apiClient.get<Client>(`/clientes/${id}`).then((r) => r.data),

  create: (data: Partial<Client>) =>
    apiClient.post<Client>('/clientes', data).then((r) => r.data),

  update: (id: number, data: Partial<Client>) =>
    apiClient.put<Client>(`/clientes/${id}`, data).then((r) => r.data),

  delete: (id: number) => apiClient.delete(`/clientes/${id}`),
};

// Categories
export const categoriesApi = {
  list: (params?: PaginationParams) =>
    apiClient.get<CategoryListResponse>('/categories', { params: params || { skip: 0, limit: 100 } }).then((r) => r.data),

  get: (id: string) => apiClient.get<Category>(`/categories/${id}`).then((r) => r.data),

  create: (data: { name: string }) =>
    apiClient.post<Category>('/categories', data).then((r) => r.data),

  update: (id: string, data: { name: string }) =>
    apiClient.put<Category>(`/categories/${id}`, data).then((r) => r.data),

  delete: (id: string) => apiClient.delete(`/categories/${id}`),

  listSubcategories: (categoryId: string, params?: PaginationParams) =>
    apiClient.get<SubcategoryListResponse>(`/categories/${categoryId}/subcategories`, {
      params: params || { skip: 0, limit: 100 },
    }).then((r) => r.data),

  createSubcategory: (categoryId: string, data: { name: string }) =>
    apiClient.post<Subcategory>(`/categories/${categoryId}/subcategories`, data).then((r) => r.data),

  updateSubcategory: (subcategoryId: string, data: { name: string }) =>
    apiClient.put<Subcategory>(`/categories/subcategories/${subcategoryId}`, data).then((r) => r.data),

  deleteSubcategory: (subcategoryId: string) =>
    apiClient.delete(`/categories/subcategories/${subcategoryId}`),
};

// Equipment
export const equipmentApi = {
  list: (params: PaginationParams & { id_cliente?: number; id_tipo_equipos?: number }) =>
    apiClient.get<EquipmentListResponse>('/equipos', { params }).then((r) => r.data),

  get: (id: number) => apiClient.get<Equipment>(`/equipos/${id}`).then((r) => r.data),

  getByQr: (qrIdentifier: string) =>
    apiClient.get<Equipment>(`/equipos/qr/${qrIdentifier}`).then((r) => r.data),

  create: (data: {
    id_tipo_equipos: number;
    id_marca: number;
    modelo: string;
    id_cliente: number;
    numero_serie?: string;
    descripcion?: string;
    condicion: string;
    accesorios?: string;
    qr_identifier?: string;
    onedrive_path?: string;
    id_subtipo?: number;
  }) => apiClient.post<Equipment>('/equipos', data).then((r) => r.data),

  update: (id: number, data: Partial<Omit<Equipment, 'id_equipos' | 'created_at' | 'updated_at'> & { id_subtipo?: number }>) =>
    apiClient.put<Equipment>(`/equipos/${id}`, data).then((r) => r.data),

  delete: (id: number) => apiClient.delete(`/equipos/${id}`),

  getQrImage: (id: number) =>
    apiClient
      .get(`/equipos/${id}/qr-image`, { responseType: 'blob' })
      .then((r) => r.data),
};

// Tipo Equipos
export const tipoEquiposApi = {
  getAll: () =>
    apiClient.get<{ items: TipoEquipo[] }>('/tipo-equipos').then((r) => r.data),
};

// Marcas
export const marcasApi = {
  getAll: () =>
    apiClient.get<{ items: Marca[] }>('/marcas').then((r) => r.data),
};

// Subtipo Equipos
export const subtipoEquiposApi = {
  getAll: (idTipoEquipo?: number) =>
    apiClient
      .get<{ items: SubtipoEquipo[] }>('/subtipo-equipos', {
        params: idTipoEquipo ? { tipo_id: idTipoEquipo } : {},
      })
      .then((r) => r.data),
};

// Service Orders
export const ordersApi = {
  list: (
    params: PaginationParams & {
      id_cliente?: number;
      id_equipo?: number;
      tipo_visita?: string;
      date_from?: string;
      date_to?: string;
    }
  ) => apiClient.get<OrdenServicioListResponse>('/ordenes-servicio', { params }).then((r) => r.data),

  get: (id: number) => apiClient.get<OrdenServicio>(`/ordenes-servicio/${id}`).then((r) => r.data),

  create: (data: {
    id_cliente: number;
    id_equipo: number;
    id_empleado: number;
    id_departamento?: number;
    solicitado_por: string;
    tipo_visita: string;
    condicion_equipo: string;
    accesorios?: string;
    fecha_realizacion: string;
    fecha_finalizacion?: string;
    falla_detectada: string;
    tarea_realizada?: string;
    horas_trabajo?: number;
    empleados_adicionales?: string;
    kilometros?: number;
    viaticos?: number;
    configuracion_equipo?: string;
  }) => apiClient.post<OrdenServicio>('/ordenes-servicio', data).then((r) => r.data),

  update: (id: number, data: Partial<OrdenServicio>) =>
    apiClient.put<OrdenServicio>(`/ordenes-servicio/${id}`, data).then((r) => r.data),

  delete: (id: number) => apiClient.delete(`/ordenes-servicio/${id}`),

  getByQr: (qrIdentifier: string) =>
    apiClient.get<OrdenServicio>(`/ordenes-servicio/qr/${qrIdentifier}`).then((r) => r.data),
};

// Employees
export const empleadosApi = {
  getAll: () =>
    apiClient.get<{ items: Empleado[] }>('/empleados').then((r) => r.data),
};

// Departments
export const departamentosApi = {
  getByCliente: (idCliente: number) =>
    apiClient.get<{ items: Departamento[] }>(`/departamentos/cliente/${idCliente}`).then((r) => r.data),
};

// Attachments
export const attachmentsApi = {
  upload: (formData: FormData) =>
    apiClient
      .post<Attachment>('/attachments/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data),

  download: (id: string) =>
    apiClient.get(`/attachments/${id}/download`, { responseType: 'blob' }).then((r) => r.data),

  listByEquipment: (equipmentId: string) =>
    apiClient.get<AttachmentListResponse>(`/attachments/equipment/${equipmentId}`).then((r) => r.data),

  listByOrder: (orderId: string) =>
    apiClient.get<AttachmentListResponse>(`/attachments/orders/${orderId}`).then((r) => r.data),

  delete: (id: string) => apiClient.delete(`/attachments/${id}`),
};

// PDF
export const pdfApi = {
  download: (orderId: number) =>
    apiClient.get(`/pdf/ordenes-servicio/${orderId}`, { responseType: 'blob' }).then((r) => r.data),

  regenerate: (orderId: number) =>
    apiClient.post(`/pdf/ordenes-servicio/${orderId}/regenerate`, { responseType: 'blob' }).then((r) => r.data),
};

// OneDrive
export const onedriveApi = {
  sync: (equipmentId: string) =>
    apiClient.post(`/onedrive/sync/${equipmentId}`).then((r) => r.data),

  status: () => apiClient.get('/onedrive/status').then((r) => r.data),
};

// Public (no auth)
export const publicApi = {
  getEquipment: (qrId: string) =>
    apiClient.get(`/equipos/qr/${qrId}`).then((r) => r.data),

  getAttachments: (equipmentId: string) =>
    apiClient
      .get<AttachmentListResponse>(`/attachments/equipment/${equipmentId}`)
      .then((r) => r.data),

  downloadAttachment: (attachmentId: string) =>
    apiClient
      .get(`/public/equipment/attachments/${attachmentId}`, { responseType: 'blob' })
      .then((r) => r.data),
};
