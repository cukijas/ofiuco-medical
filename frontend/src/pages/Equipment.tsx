import { useState, type FormEvent, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { equipmentApi, clientsApi, categoriesApi } from '../api/endpoints';
import type { Equipment } from '../types';
import { DataTable } from '../components/DataTable';
import { FormModal } from '../components/FormModal';
import { DeleteConfirm } from '../components/DeleteConfirm';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useAuth } from '../hooks/useAuth';

interface EquipmentForm {
  client_id: string;
  category_id: string;
  subcategory_id: string;
  brand: string;
  model: string;
  serial_number: string;
}

const emptyForm: EquipmentForm = {
  client_id: '',
  category_id: '',
  subcategory_id: '',
  brand: '',
  model: '',
  serial_number: '',
};

export function EquipmentPage() {
  const { isAdmin } = useAuth();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Equipment | null>(null);
  const [deleting, setDeleting] = useState<Equipment | null>(null);
  const [formData, setFormData] = useState<EquipmentForm>(emptyForm);
  const [filterClient, setFilterClient] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [error, setError] = useState('');
  const pageSize = 20;

  // Fetch equipment list
  const { data, isLoading } = useQuery({
    queryKey: ['equipment', page, filterClient, filterCategory],
    queryFn: () =>
      equipmentApi.list({
        skip: page * pageSize,
        limit: pageSize,
        ...(filterClient ? { client_id: filterClient } : {}),
        ...(filterCategory ? { category_id: filterCategory } : {}),
      }),
  });

  // Fetch clients for dropdown
  const { data: clientsData } = useQuery({
    queryKey: ['clients-list'],
    queryFn: () => clientsApi.list({ skip: 0, limit: 100 }),
  });

  // Fetch categories from API
  const { data: categoriesData } = useQuery({
    queryKey: ['categories-list'],
    queryFn: () => categoriesApi.list({ skip: 0, limit: 100 }),
  });

  // Fetch subcategories when category is selected
  const { data: subcategoriesData } = useQuery({
    queryKey: ['subcategories-list', formData.category_id],
    queryFn: () => categoriesApi.listSubcategories(formData.category_id, { skip: 0, limit: 100 }),
    enabled: !!formData.category_id,
  });

  // Reset subcategory when category changes
  useEffect(() => {
    if (formData.category_id) {
      setFormData((prev) => ({ ...prev, subcategory_id: '' }));
    }
  }, [formData.category_id]);

  // Fetch subcategories for filter dropdown
  const [filterSubcategory, setFilterSubcategory] = useState('');
  const { data: filterSubcategoriesData } = useQuery({
    queryKey: ['subcategories-filter', filterCategory],
    queryFn: () => categoriesApi.listSubcategories(filterCategory, { skip: 0, limit: 100 }),
    enabled: !!filterCategory,
  });

  const createMutation = useMutation({
    mutationFn: (d: EquipmentForm) =>
      equipmentApi.create({
        client_id: d.client_id,
        category_id: d.category_id,
        subcategory_id: d.subcategory_id || undefined,
        brand: d.brand,
        model: d.model,
        serial_number: d.serial_number,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipment'] });
      setShowForm(false);
      setFormData(emptyForm);
    },
    onError: (err: Error) => setError(err.message),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data: d }: { id: string; data: EquipmentForm }) =>
      equipmentApi.update(id, {
        client_id: d.client_id || undefined,
        category_id: d.category_id || undefined,
        subcategory_id: d.subcategory_id || undefined,
        brand: d.brand || undefined,
        model: d.model || undefined,
        serial_number: d.serial_number || undefined,
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
    mutationFn: (id: string) => equipmentApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipment'] });
      setDeleting(null);
    },
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (editing) {
      updateMutation.mutate({ id: editing.id, data: formData });
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
      client_id: eq.client_id,
      category_id: eq.category_id,
      subcategory_id: eq.subcategory_id || '',
      brand: eq.brand,
      model: eq.model,
      serial_number: eq.serial_number,
    });
    setShowForm(true);
  };

  const downloadQr = async (eq: Equipment) => {
    const blob = await equipmentApi.getQrImage(eq.id);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `qr-${eq.serial_number}.png`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getClientName = (id: string) => {
    return clientsData?.items.find((c) => c.id === id)?.name || id;
  };

  const columns = [
    { key: 'brand', header: 'Marca', render: (item: unknown) => { const e = item as Equipment; return `${e.brand} ${e.model}`; } },
    { key: 'serial_number', header: 'Serie' },
    { key: 'client_id', header: 'Cliente', render: (item: unknown) => getClientName((item as Equipment).client_id) },
    { key: 'category_name', header: 'Categoría', render: (item: unknown) => (item as Equipment).category_name || (item as Equipment).category_id },
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
        <h1 className="text-2xl font-bold text-gray-900">Equipamiento</h1>
        <button onClick={openCreate} className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700">
          Nuevo Equipamiento
        </button>
      </div>

      <div className="flex gap-3">
        <select value={filterClient} onChange={(e) => { setFilterClient(e.target.value); setPage(0); }} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
          <option value="">Todos los clientes</option>
          {clientsData?.items.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
        <select value={filterCategory} onChange={(e) => { setFilterCategory(e.target.value); setFilterSubcategory(''); setPage(0); }} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
          <option value="">Todas las categorías</option>
          {categoriesData?.items.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
        {filterCategory && (
          <select value={filterSubcategory} onChange={(e) => { setFilterSubcategory(e.target.value); setPage(0); }} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
            <option value="">Todas las subcategorías</option>
            {filterSubcategoriesData?.items.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        )}
      </div>

      <DataTable
        data={(data?.items || []) as unknown[]}
        columns={columns}
        total={data?.total || 0}
        page={page}
        pageSize={pageSize}
        onPageChange={setPage}
      />

      <FormModal open={showForm} title={editing ? 'Editar Equipamiento' : 'Nuevo Equipamiento'} onClose={() => { setShowForm(false); setEditing(null); }}>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}

          <div>
            <label className="block text-sm font-medium text-gray-700">Cliente *</label>
            <select required value={formData.client_id} onChange={(e) => setFormData({ ...formData, client_id: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
              <option value="">Seleccionar cliente</option>
              {clientsData?.items.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Categoría *</label>
              <select required value={formData.category_id} onChange={(e) => setFormData({ ...formData, category_id: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
                <option value="">Seleccionar categoría</option>
                {categoriesData?.items.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Subcategoría</label>
              <select value={formData.subcategory_id} onChange={(e) => setFormData({ ...formData, subcategory_id: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" disabled={!formData.category_id}>
                <option value="">Seleccionar subcategoría</option>
                {subcategoriesData?.items.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Marca *</label>
              <input required value={formData.brand} onChange={(e) => setFormData({ ...formData, brand: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Modelo *</label>
              <input required value={formData.model} onChange={(e) => setFormData({ ...formData, model: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Número de Serie *</label>
            <input required value={formData.serial_number} onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
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
        title="Eliminar Equipamiento"
        message={`¿Estás seguro de eliminar "${deleting?.brand} ${deleting?.model}"? Esta acción no se puede deshacer.`}
        onConfirm={() => deleting && deleteMutation.mutate(deleting.id)}
        onCancel={() => setDeleting(null)}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}