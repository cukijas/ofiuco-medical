export type RoleEnum = 'admin' | 'technician';
export type StatusEnum = 'draft' | 'in_progress' | 'completed' | 'delivered';
export type AttachmentTypeEnum = 'report' | 'photo' | 'manual' | 'other';

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: RoleEnum;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Client {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  city: string | null;
  province: string | null;
  postal_code: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClientListResponse {
  items: Client[];
  total: number;
  skip: number;
  limit: number;
}

export interface Equipment {
  id: string;
  client_id: string;
  category_id: string;
  subcategory_id: string | null;
  category_name: string | null;
  subcategory_name: string | null;
  brand: string;
  model: string;
  serial_number: string;
  qr_code: string;
  onedrive_path: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface EquipmentListResponse {
  items: Equipment[];
  total: number;
  skip: number;
  limit: number;
}

export interface Part {
  id: string;
  service_order_id: string;
  part_name: string;
  part_number: string | null;
  quantity: number;
  unit_cost: number | null;
  created_at: string;
  updated_at: string;
}

export interface ServiceOrder {
  id: string;
  order_number: string;
  client_id: string;
  equipment_id: string;
  technician_id: string;
  status: StatusEnum;
  description: string | null;
  diagnosis: string | null;
  solution: string | null;
  service_date: string | null;
  next_service_date: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  parts: Part[];
}

export interface OrderListResponse {
  items: ServiceOrder[];
  total: number;
  skip: number;
  limit: number;
}

export interface Attachment {
  id: string;
  file_name: string;
  file_type: string;
  onedrive_path: string | null;
  uploaded_by: string;
  equipment_id: string | null;
  service_order_id: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AttachmentListResponse {
  items: Attachment[];
  total: number;
}

export interface Category {
  id: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CategoryListResponse {
  items: Category[];
  total: number;
  skip: number;
  limit: number;
}

export interface Subcategory {
  id: string;
  category_id: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SubcategoryListResponse {
  items: Subcategory[];
  total: number;
  skip: number;
  limit: number;
}

export interface PaginationParams {
  skip: number;
  limit: number;
}
