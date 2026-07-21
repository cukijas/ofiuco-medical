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

export type TipoCliente = 'fisica' | 'juridica';

export interface Client {
  id_cliente: number;
  tipo_cliente: TipoCliente;
  nombre: string;
  telefono: string | null;
  email: string | null;
  razon_social: string | null;
  cuit: string | null;
  obra_social: string | null;
  direccion: string | null;
  localidad: string | null;
  dni: string | null;
  created_at: string;
  updated_at: string;
}

export interface ClientListResponse {
  items: Client[];
  total: number;
  skip: number;
  limit: number;
}

export interface TipoEquipo {
  id_tipo_equipos: number;
  nombre: string;
}

export interface Marca {
  id_marca: number;
  nombre: string;
}

export interface SubtipoEquipo {
  id_subtipo: number;
  id_tipo_equipos: number;
  nombre: string;
}

export type CondicionEquipo = 'nuevo' | 'usado' | 'otro';

export interface Equipment {
  id_equipos: number;
  id_tipo_equipos: number;
  id_marca: number;
  modelo: string;
  id_cliente: number;
  numero_serie: string | null;
  descripcion: string | null;
  condicion: CondicionEquipo;
  accesorios: string | null;
  qr_identifier: string;
  onedrive_path: string | null;
  created_at: string;
  updated_at: string;
}

export interface EquipmentListResponse {
  items: Equipment[];
  total: number;
  skip: number;
  limit: number;
}

export type TipoVisita = 'normal' | 'por contrato' | 'por garantía';
export type CondicionEquipoOrden = 'nuevo' | 'usado' | 'otro';

export interface OrdenServicio {
  id_orden: number;
  numero_orden: string;
  numero_referencia: string;
  id_cliente: number;
  id_equipo: number;
  id_empleado: number;
  id_departamento: number | null;
  solicitado_por: string;
  tipo_visita: TipoVisita;
  condicion_equipo: CondicionEquipoOrden;
  accesorios: string | null;
  fecha_realizacion: string;
  fecha_finalizacion: string | null;
  falla_detectada: string | null;
  tarea_realizada: string | null;
  horas_trabajo: number | null;
  empleados_adicionales: string | null;
  kilometros: number | null;
  viaticos: number | null;
  configuracion_equipo: string | null;
  qr_identifier: string;
  onedrive_path: string | null;
  created_at: string;
  updated_at: string;
}

export interface OrdenServicioListResponse {
  items: OrdenServicio[];
  total: number;
  skip: number;
  limit: number;
}

export interface Empleado {
  id_empleado: number;
  nombre: string;
  especialidad: string | null;
}

export interface Departamento {
  id_departamento: number;
  id_cliente: number;
  nombre: string;
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
