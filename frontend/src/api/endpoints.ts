import apiClient from './client';
import type {
  TokenResponse,
  User,
  Client,
  ClientListResponse,
  Equipment,
  EquipmentListResponse,
  ServiceOrder,
  OrderListResponse,
  Part,
  Attachment,
  AttachmentListResponse,
  PaginationParams,
  Category,
  CategoryListResponse,
  Subcategory,
  SubcategoryListResponse,
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
    apiClient.get<ClientListResponse>('/clients', { params }).then((r) => r.data),

  get: (id: string) => apiClient.get<Client>(`/clients/${id}`).then((r) => r.data),

  create: (data: Partial<Client>) =>
    apiClient.post<Client>('/clients', data).then((r) => r.data),

  update: (id: string, data: Partial<Client>) =>
    apiClient.put<Client>(`/clients/${id}`, data).then((r) => r.data),

  delete: (id: string) => apiClient.delete(`/clients/${id}`),
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
  list: (params: PaginationParams & { client_id?: string; category_id?: string }) =>
    apiClient.get<EquipmentListResponse>('/equipment', { params }).then((r) => r.data),

  get: (id: string) => apiClient.get<Equipment>(`/equipment/${id}`).then((r) => r.data),

  getByQr: (qrCode: string) =>
    apiClient.get<Equipment>(`/equipment/qr/${qrCode}`).then((r) => r.data),

  create: (data: {
    client_id: string;
    category_id: string;
    subcategory_id?: string;
    brand: string;
    model: string;
    serial_number: string;
  }) => apiClient.post<Equipment>('/equipment', data).then((r) => r.data),

  update: (id: string, data: Partial<Equipment>) =>
    apiClient.put<Equipment>(`/equipment/${id}`, data).then((r) => r.data),

  delete: (id: string) => apiClient.delete(`/equipment/${id}`),

  getQrImage: (id: string) =>
    apiClient
      .get(`/equipment/${id}/qr-image`, { responseType: 'blob' })
      .then((r) => r.data),
};

// Service Orders
export const ordersApi = {
  list: (
    params: PaginationParams & {
      client_id?: string;
      equipment_id?: string;
      status?: string;
      date_from?: string;
      date_to?: string;
    }
  ) => apiClient.get<OrderListResponse>('/orders', { params }).then((r) => r.data),

  get: (id: string) => apiClient.get<ServiceOrder>(`/orders/${id}`).then((r) => r.data),

  create: (data: {
    client_id: string;
    equipment_id: string;
    technician_id?: string;
    description?: string;
    service_date?: string;
  }) => apiClient.post<ServiceOrder>('/orders', data).then((r) => r.data),

  update: (id: string, data: Partial<ServiceOrder>) =>
    apiClient.put<ServiceOrder>(`/orders/${id}`, data).then((r) => r.data),

  delete: (id: string) => apiClient.delete(`/orders/${id}`),

  updateStatus: (id: string, status: string) =>
    apiClient
      .patch<ServiceOrder>(`/orders/${id}/status`, { status })
      .then((r) => r.data),

  addPart: (orderId: string, data: { part_name: string; part_number?: string; quantity: number; unit_cost?: number }) =>
    apiClient.post<Part>(`/orders/${orderId}/parts`, data).then((r) => r.data),

  removePart: (orderId: string, partId: string) =>
    apiClient.delete(`/orders/${orderId}/parts/${partId}`),
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
  download: (orderId: string) =>
    apiClient.get(`/pdf/orders/${orderId}`, { responseType: 'blob' }).then((r) => r.data),

  regenerate: (orderId: string) =>
    apiClient.post(`/pdf/orders/${orderId}/regenerate`, { responseType: 'blob' }).then((r) => r.data),
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
    apiClient.get(`/equipment/qr/${qrId}`).then((r) => r.data),

  getAttachments: (equipmentId: string) =>
    apiClient
      .get<AttachmentListResponse>(`/attachments/equipment/${equipmentId}`)
      .then((r) => r.data),

  downloadAttachment: (attachmentId: string) =>
    apiClient
      .get(`/public/equipment/attachments/${attachmentId}`, { responseType: 'blob' })
      .then((r) => r.data),
};
