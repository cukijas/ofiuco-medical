import { useState, type FormEvent } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { clientsApi } from '../api/endpoints';
import type { Client, TipoCliente } from '../types';
import { DataTable } from '../components/DataTable';
import { FormModal } from '../components/FormModal';
import { DeleteConfirm } from '../components/DeleteConfirm';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useAuth } from '../hooks/useAuth';

const emptyForm: Partial<Client> = {
  tipo_cliente: 'fisica',
  nombre: '',
  telefono: '',
  email: '',
  razon_social: '',
  cuit: '',
  obra_social: '',
  direccion: '',
  localidad: '',
  dni: '',
};

export function Clients() {
  const { isAdmin } = useAuth();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Client | null>(null);
  const [deleting, setDeleting] = useState<Client | null>(null);
  const [formData, setFormData] = useState<Partial<Client>>(emptyForm);
  const [error, setError] = useState('');
  const pageSize = 20;

  const { data, isLoading } = useQuery({
    queryKey: ['clients', page],
    queryFn: () => clientsApi.list({ skip: page * pageSize, limit: pageSize }),
  });

  const createMutation = useMutation({
    mutationFn: (d: Partial<Client>) => clientsApi.create(d),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      setShowForm(false);
      setFormData(emptyForm);
    },
    onError: (err: Error) => setError(err.message),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data: d }: { id: number; data: Partial<Client> }) =>
      clientsApi.update(id, d),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      setShowForm(false);
      setEditing(null);
      setFormData(emptyForm);
    },
    onError: (err: Error) => setError(err.message),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => clientsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      setDeleting(null);
    },
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (editing) {
      updateMutation.mutate({ id: editing.id_cliente, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const openCreate = () => {
    setEditing(null);
    setFormData(emptyForm);
    setShowForm(true);
  };

  const openEdit = (client: Client) => {
    setEditing(client);
    setFormData(client);
    setShowForm(true);
  };

  const isJuridica = formData.tipo_cliente === 'juridica';

  const columns = [
    { key: 'nombre', header: 'Nombre' },
    {
      key: 'tipo_cliente',
      header: 'Tipo',
      render: (item: unknown) => {
        const c = item as Client;
        return c.tipo_cliente === 'juridica' ? 'Jurídica' : 'Física';
      },
    },
    { key: 'email', header: 'Email', render: (item: unknown) => (item as Client).email || '-' },
    { key: 'telefono', header: 'Teléfono', render: (item: unknown) => (item as Client).telefono || '-' },
    { key: 'localidad', header: 'Localidad', render: (item: unknown) => (item as Client).localidad || '-' },
    {
      key: 'actions',
      header: 'Acciones',
      render: (item: unknown) => {
        const c = item as Client;
        return (
          <div className="flex gap-2">
            <button
              onClick={(e) => { e.stopPropagation(); openEdit(c); }}
              className="text-sm text-primary-600 hover:text-primary-800"
            >
              Editar
            </button>
            {isAdmin && (
              <button
                onClick={(e) => { e.stopPropagation(); setDeleting(c); }}
                className="text-sm text-red-600 hover:text-red-800"
              >
                Eliminar
              </button>
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
        <h1 className="text-2xl font-bold text-gray-900">Clientes</h1>
        <button
          onClick={openCreate}
          className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
        >
          Nuevo Cliente
        </button>
      </div>

      <DataTable
        data={(data?.items || []) as unknown[]}
        columns={columns}
        total={data?.total || 0}
        page={page}
        pageSize={pageSize}
        onPageChange={setPage}
      />

      <FormModal
        open={showForm}
        title={editing ? 'Editar Cliente' : 'Nuevo Cliente'}
        onClose={() => { setShowForm(false); setEditing(null); }}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}

          <div>
            <label className="block text-sm font-medium text-gray-700">Tipo de Cliente *</label>
            <select
              required
              value={formData.tipo_cliente || 'fisica'}
              onChange={(e) => setFormData({ ...formData, tipo_cliente: e.target.value as TipoCliente })}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              <option value="fisica">Persona Física</option>
              <option value="juridica">Persona Jurídica</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Nombre *</label>
            <input
              required
              value={formData.nombre || ''}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                value={formData.email || ''}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Teléfono</label>
              <input
                value={formData.telefono || ''}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
          </div>

          {isJuridica ? (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700">Razón Social</label>
                <input
                  value={formData.razon_social || ''}
                  onChange={(e) => setFormData({ ...formData, razon_social: e.target.value })}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">CUIT</label>
                  <input
                    value={formData.cuit || ''}
                    onChange={(e) => setFormData({ ...formData, cuit: e.target.value })}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Obra Social</label>
                  <input
                    value={formData.obra_social || ''}
                    onChange={(e) => setFormData({ ...formData, obra_social: e.target.value })}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                  />
                </div>
              </div>
            </>
          ) : (
            <div>
              <label className="block text-sm font-medium text-gray-700">DNI</label>
              <input
                value={formData.dni || ''}
                onChange={(e) => setFormData({ ...formData, dni: e.target.value })}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700">Dirección</label>
            <input
              value={formData.direccion || ''}
              onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Localidad</label>
            <input
              value={formData.localidad || ''}
              onChange={(e) => setFormData({ ...formData, localidad: e.target.value })}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => { setShowForm(false); setEditing(null); }}
              className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending}
              className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
            >
              {createMutation.isPending || updateMutation.isPending ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </FormModal>

      <DeleteConfirm
        open={!!deleting}
        title="Eliminar Cliente"
        message={`¿Estás seguro de eliminar a "${deleting?.nombre}"? Esta acción no se puede deshacer.`}
        onConfirm={() => deleting && deleteMutation.mutate(deleting.id_cliente)}
        onCancel={() => setDeleting(null)}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}
