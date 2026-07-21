import { useState, type FormEvent } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  equipmentApi,
  clientsApi,
  tipoEquiposApi,
  marcasApi,
} from '../api/endpoints';
import type { Equipment, CondicionEquipo } from '../types';
import { DataTable } from '../components/DataTable';
import { FormModal } from '../components/FormModal';
import { DeleteConfirm } from '../components/DeleteConfirm';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useAuth } from '../hooks/useAuth';

interface EquipmentForm {
  id_tipo_equipos: string;
  id_marca: string;
  modelo: string;
  id_cliente: string;
  numero_serie: string;
  descripcion: string;
  condicion: CondicionEquipo;
  accesorios: string;
  qr_identifier: string;
  onedrive_path: string;
}

const emptyForm: EquipmentForm = {
  id_tipo_equipos: '',
  id_marca: '',
  modelo: '',
  id_cliente: '',
  numero_serie: '',
  descripcion: '',
  condicion: 'nuevo',
  accesorios: '',
  qr_identifier: '',
  onedrive_path: '',
};

const CONDICION_OPTIONS: { value: CondicionEquipo; label: string }[] = [
  { value: 'nuevo', label: 'Nuevo' },
  { value: 'usado', label: 'Usado' },
  { value: 'otro', label: 'Otro' },
];

export function EquipmentPage() {
  const { isAdmin } = useAuth();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Equipment | null>(null);
  const [deleting, setDeleting] = useState<Equipment | null>(null);
  const [formData, setFormData] = useState<EquipmentForm>(emptyForm);
  const [filterClient, setFilterClient] = useState('');
  const [filterTipo, setFilterTipo] = useState('');
  const [error, setError] = useState('');
  const pageSize = 20;

  const { data, isLoading } = useQuery({
    queryKey: ['equipment', page, filterClient, filterTipo],
    queryFn: () =>
      equipmentApi.list({
        skip: page * pageSize,
        limit: pageSize,
        ...(filterClient ? { id_cliente: Number(filterClient) } : {}),
        ...(filterTipo ? { id_tipo_equipos: Number(filterTipo) } : {}),
      }),
  });

  const { data: clientsData } = useQuery({
    queryKey: ['clients-list'],
    queryFn: () => clientsApi.list({ skip: 0, limit: 100 }),
  });

  const { data: tiposData } = useQuery({
    queryKey: ['tipos-equipos'],
    queryFn: () => tipoEquiposApi.getAll(),
  });

  const { data: marcasData } = useQuery({
    queryKey: ['marcas'],
    queryFn: () => marcasApi.getAll(),
  });

  const createMutation = useMutation({
    mutationFn: (d: EquipmentForm) =>
      equipmentApi.create({
        id_tipo_equipos: Number(d.id_tipo_equipos),
        id_marca: Number(d.id_marca),
        modelo: d.modelo,
        id_cliente: Number(d.id_cliente),
        numero_serie: d.numero_serie || undefined,
        descripcion: d.descripcion || undefined,
        condicion: d.condicion,
        accesorios: d.accesorios || undefined,
        qr_identifier: d.qr_identifier || undefined,
        onedrive_path: d.onedrive_path || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipment'] });
      setShowForm(false);
      setFormData(emptyForm);
    },
    onError: (err: Error) => setError(err.message),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data: d }: { id: number; data: EquipmentForm }) =>
      equipmentApi.update(id, {
        id_tipo_equipos: Number(d.id_tipo_equipos),
        id_marca: Number(d.id_marca),
        modelo: d.modelo,
        id_cliente: Number(d.id_cliente),
        numero_serie: d.numero_serie || undefined,
        descripcion: d.descripcion || undefined,
        condicion: d.condicion,
        accesorios: d.accesorios || undefined,
        qr_identifier: d.qr_identifier || undefined,
        onedrive_path: d.onedrive_path || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipment'] });
      setShowForm(false);
      setEditing(null);
      setFormData(emptyForm);
    },
    onError: (err: Error) => setError(err.message),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => equipmentApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipment'] });
      setDeleting(null);
    },
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (editing) {
      updateMutation.mutate({ id: editing.id_equipos, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const openCreate = () => {
    setEditing(null);
    setFormData(emptyForm);
    setShowForm(true);
  };

  const openEdit = (eq: Equipment) => {
    setEditing(eq);
    setFormData({
      id_tipo_equipos: eq.id_tipo_equipos.toString(),
      id_marca: eq.id_marca.toString(),
      modelo: eq.modelo,
      id_cliente: eq.id_cliente.toString(),
      numero_serie: eq.numero_serie || '',
      descripcion: eq.descripcion || '',
      condicion: eq.condicion,
      accesorios: eq.accesorios || '',
      qr_identifier: eq.qr_identifier || '',
      onedrive_path: eq.onedrive_path || '',
    });
    setShowForm(true);
  };

  const downloadQr = async (eq: Equipment) => {
    const blob = await equipmentApi.getQrImage(eq.id_equipos);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `qr-${eq.numero_serie || eq.modelo}.png`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getClientName = (id: number) => {
    return clientsData?.items.find((c) => c.id_cliente === id)?.nombre || id;
  };

  const getTipoName = (id: number) => {
    return tiposData?.items.find((t) => t.id_tipo_equipos === id)?.nombre || id;
  };

  const getMarcaName = (id: number) => {
    return marcasData?.items.find((m) => m.id_marca === id)?.nombre || id;
  };

  const getCondicionLabel = (condicion: CondicionEquipo) => {
    return CONDICION_OPTIONS.find((c) => c.value === condicion)?.label || condicion;
  };

  const columns = [
    { key: 'id_tipo_equipos', header: 'Tipo', render: (item: unknown) => getTipoName((item as Equipment).id_tipo_equipos) },
    { key: 'id_marca', header: 'Marca', render: (item: unknown) => getMarcaName((item as Equipment).id_marca) },
    { key: 'modelo', header: 'Modelo' },
    { key: 'numero_serie', header: 'N° Serie' },
    { key: 'id_cliente', header: 'Cliente', render: (item: unknown) => getClientName((item as Equipment).id_cliente) },
    { key: 'condicion', header: 'Condición', render: (item: unknown) => getCondicionLabel((item as Equipment).condicion) },
    {
      key: 'actions',
      header: 'Acciones',
      className: 'w-48',
      render: (item: unknown) => {
        const e = item as Equipment;
        return (
          <div className="flex gap-2">
            <button onClick={(ev) => { ev.stopPropagation(); openEdit(e); }} className="text-sm text-primary-600 hover:text-primary-800">Editar</button>
            <button onClick={(ev) => { ev.stopPropagation(); downloadQr(e); }} className="text-sm text-green-600 hover:text-green-800">QR</button>
            {isAdmin && (
              <button onClick={(ev) => { ev.stopPropagation(); setDeleting(e); }} className="text-sm text-red-600 hover:text-red-800">Eliminar</button>
            )}
          </div>
        );
      },
    },
  ];

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Equipo</h1>
        <button onClick={openCreate} className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700">
          Nuevo Equipo
        </button>
      </div>

      <div className="flex gap-3">
        <select value={filterClient} onChange={(e) => { setFilterClient(e.target.value); setPage(0); }} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
          <option value="">Todos los clientes</option>
          {clientsData?.items.map((c) => (
            <option key={c.id_cliente} value={c.id_cliente}>{c.nombre}</option>
          ))}
        </select>
        <select value={filterTipo} onChange={(e) => { setFilterTipo(e.target.value); setPage(0); }} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
          <option value="">Todos los tipos</option>
          {tiposData?.items.map((t) => (
            <option key={t.id_tipo_equipos} value={t.id_tipo_equipos}>{t.nombre}</option>
          ))}
        </select>
      </div>

      <DataTable
        data={(data?.items || []) as unknown[]}
        columns={columns}
        total={data?.total || 0}
        page={page}
        pageSize={pageSize}
        onPageChange={setPage}
      />

      <FormModal open={showForm} title={editing ? 'Editar Equipo' : 'Nuevo Equipo'} onClose={() => { setShowForm(false); setEditing(null); }}>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Cliente *</label>
              <select required value={formData.id_cliente} onChange={(e) => setFormData({ ...formData, id_cliente: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
                <option value="">Seleccionar cliente</option>
                {clientsData?.items.map((c) => (
                  <option key={c.id_cliente} value={c.id_cliente}>{c.nombre}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Tipo de Equipo *</label>
              <select required value={formData.id_tipo_equipos} onChange={(e) => setFormData({ ...formData, id_tipo_equipos: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
                <option value="">Seleccionar tipo</option>
                {tiposData?.items.map((t) => (
                  <option key={t.id_tipo_equipos} value={t.id_tipo_equipos}>{t.nombre}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Marca *</label>
              <select required value={formData.id_marca} onChange={(e) => setFormData({ ...formData, id_marca: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
                <option value="">Seleccionar marca</option>
                {marcasData?.items.map((m) => (
                  <option key={m.id_marca} value={m.id_marca}>{m.nombre}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Modelo *</label>
              <input required value={formData.modelo} onChange={(e) => setFormData({ ...formData, modelo: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Número de Serie</label>
              <input value={formData.numero_serie} onChange={(e) => setFormData({ ...formData, numero_serie: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Condición *</label>
              <select required value={formData.condicion} onChange={(e) => setFormData({ ...formData, condicion: e.target.value as CondicionEquipo })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
                {CONDICION_OPTIONS.map((c) => (
                  <option key={c.value} value={c.value}>{c.label}</option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Identificador QR</label>
            <input value={formData.qr_identifier} onChange={(e) => setFormData({ ...formData, qr_identifier: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
            <p className="mt-1 text-xs text-gray-500">(se genera automáticamente al vincular OneDrive)</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Ruta OneDrive</label>
            <input value={formData.onedrive_path} onChange={(e) => setFormData({ ...formData, onedrive_path: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" placeholder="Código o ruta de la carpeta OneDrive" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Descripción</label>
            <textarea value={formData.descripcion} onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })} rows={3} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Accesorios</label>
            <textarea value={formData.accesorios} onChange={(e) => setFormData({ ...formData, accesorios: e.target.value })} rows={2} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" placeholder="Accesorios incluidos con el equipo" />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => { setShowForm(false); setEditing(null); }} className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
              Cancelar
            </button>
            <button type="submit" disabled={createMutation.isPending || updateMutation.isPending} className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50">
              {createMutation.isPending || updateMutation.isPending ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </FormModal>

      <DeleteConfirm
        open={!!deleting}
        title="Eliminar Equipo"
        message={`¿Estás seguro de eliminar "${deleting?.numero_serie || deleting?.modelo}"? Esta acción no se puede deshacer.`}
        onConfirm={() => deleting && deleteMutation.mutate(deleting.id_equipos)}
        onCancel={() => setDeleting(null)}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}
