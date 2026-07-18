import { useState, type FormEvent } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ordersApi, clientsApi, equipmentApi, pdfApi } from '../api/endpoints';
import type { ServiceOrder, StatusEnum } from '../types';
import { DataTable } from '../components/DataTable';
import { FormModal } from '../components/FormModal';
import { DeleteConfirm } from '../components/DeleteConfirm';
import { StatusBadge } from '../components/StatusBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useAuth } from '../hooks/useAuth';

const statusFlow: StatusEnum[] = ['draft', 'in_progress', 'completed', 'delivered'];

interface OrderForm {
  client_id: string;
  equipment_id: string;
  description: string;
  service_date: string;
}

const emptyForm: OrderForm = {
  client_id: '',
  equipment_id: '',
  description: '',
  service_date: '',
};

interface PartForm {
  part_name: string;
  part_number: string;
  quantity: number;
  unit_cost: string;
}

const emptyPartForm: PartForm = {
  part_name: '',
  part_number: '',
  quantity: 1,
  unit_cost: '',
};

export function ServiceOrders() {
  const { isAdmin } = useAuth();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<ServiceOrder | null>(null);
  const [deleting, setDeleting] = useState<ServiceOrder | null>(null);
  const [viewingParts, setViewingParts] = useState<ServiceOrder | null>(null);
  const [partForm, setPartForm] = useState<PartForm>(emptyPartForm);
  const [formData, setFormData] = useState<OrderForm>(emptyForm);
  const [filterStatus, setFilterStatus] = useState('');
  const [filterClient, setFilterClient] = useState('');
  const [error, setError] = useState('');
  const pageSize = 20;

  const { data, isLoading } = useQuery({
    queryKey: ['orders', page, filterStatus, filterClient],
    queryFn: () =>
      ordersApi.list({
        skip: page * pageSize,
        limit: pageSize,
        ...(filterStatus ? { status: filterStatus } : {}),
        ...(filterClient ? { client_id: filterClient } : {}),
      }),
  });

  const { data: clientsData } = useQuery({
    queryKey: ['clients-list'],
    queryFn: () => clientsApi.list({ skip: 0, limit: 100 }),
  });

  const { data: equipData } = useQuery({
    queryKey: ['equipment-list'],
    queryFn: () => equipmentApi.list({ skip: 0, limit: 100 }),
  });

  const createMutation = useMutation({
    mutationFn: (d: OrderForm) =>
      ordersApi.create({
        client_id: d.client_id,
        equipment_id: d.equipment_id,
        description: d.description || undefined,
        service_date: d.service_date || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      setShowForm(false);
      setFormData(emptyForm);
    },
    onError: (err: Error) => setError(err.message),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data: d }: { id: string; data: OrderForm }) =>
      ordersApi.update(id, {
        client_id: d.client_id || undefined,
        equipment_id: d.equipment_id || undefined,
        description: d.description || undefined,
        service_date: d.service_date || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      setShowForm(false);
      setEditing(null);
      setFormData(emptyForm);
    },
    onError: (err: Error) => setError(err.message),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => ordersApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      setDeleting(null);
    },
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => ordersApi.updateStatus(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['orders'] }),
  });

  const addPartMutation = useMutation({
    mutationFn: ({ orderId, data: d }: { orderId: string; data: PartForm }) =>
      ordersApi.addPart(orderId, {
        part_name: d.part_name,
        part_number: d.part_number || undefined,
        quantity: d.quantity,
        unit_cost: d.unit_cost ? parseFloat(d.unit_cost) : undefined,
      }),
    onSuccess: () => {
      if (viewingParts) {
        queryClient.invalidateQueries({ queryKey: ['orders'] });
        setPartForm(emptyPartForm);
      }
    },
  });

  const removePartMutation = useMutation({
    mutationFn: ({ orderId, partId }: { orderId: string; partId: string }) =>
      ordersApi.removePart(orderId, partId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['orders'] }),
  });

  const downloadPdf = async (orderId: string) => {
    const blob = await pdfApi.download(orderId);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `orden-${orderId}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };

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

  const openEdit = (order: ServiceOrder) => {
    setEditing(order);
    setFormData({
      client_id: order.client_id,
      equipment_id: order.equipment_id,
      description: order.description || '',
      service_date: order.service_date || '',
    });
    setShowForm(true);
  };

  const getClientName = (id: string) => clientsData?.items.find((c) => c.id === id)?.name || id;
  const getEquipmentInfo = (id: string) => {
    const eq = equipData?.items.find((e) => e.id === id);
    return eq ? `${eq.brand} ${eq.model}` : id;
  };

  const nextStatus = (current: StatusEnum): StatusEnum | null => {
    const idx = statusFlow.indexOf(current);
    return idx >= 0 && idx < statusFlow.length - 1 ? statusFlow[idx + 1] : null;
  };

  const columns = [
    { key: 'order_number', header: 'Nº Orden' },
    { key: 'client_id', header: 'Cliente', render: (item: unknown) => getClientName((item as ServiceOrder).client_id) },
    { key: 'equipment_id', header: 'Equipamiento', render: (item: unknown) => getEquipmentInfo((item as ServiceOrder).equipment_id) },
    { key: 'status', header: 'Estado', render: (item: unknown) => <StatusBadge status={(item as ServiceOrder).status} /> },
    { key: 'service_date', header: 'Fecha', render: (item: unknown) => (item as ServiceOrder).service_date || '-' },
    {
      key: 'actions',
      header: 'Acciones',
      className: 'w-56',
      render: (item: unknown) => {
        const o = item as ServiceOrder;
        const next = nextStatus(o.status as StatusEnum);
        return (
          <div className="flex flex-wrap gap-1">
            <button onClick={(ev) => { ev.stopPropagation(); openEdit(o); }} className="text-sm text-primary-600 hover:text-primary-800">Editar</button>
            <button onClick={(ev) => { ev.stopPropagation(); setViewingParts(o); }} className="text-sm text-blue-600 hover:text-blue-800">Partes</button>
            <button onClick={(ev) => { ev.stopPropagation(); downloadPdf(o.id); }} className="text-sm text-green-600 hover:text-green-800">PDF</button>
            {next && (
              <button onClick={(ev) => { ev.stopPropagation(); statusMutation.mutate({ id: o.id, status: next }); }} className="text-sm text-orange-600 hover:text-orange-800 capitalize">
                → {next.replace('_', ' ')}
              </button>
            )}
            {isAdmin && (
              <button onClick={(ev) => { ev.stopPropagation(); setDeleting(o); }} className="text-sm text-red-600 hover:text-red-800">Eliminar</button>
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
        <h1 className="text-2xl font-bold text-gray-900">Órdenes de Servicio</h1>
        <button onClick={openCreate} className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700">
          Nueva Orden
        </button>
      </div>

      <div className="flex gap-3">
        <select value={filterStatus} onChange={(e) => { setFilterStatus(e.target.value); setPage(0); }} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
          <option value="">Todos los estados</option>
          {statusFlow.map((s) => (
            <option key={s} value={s}>{s.replace('_', ' ')}</option>
          ))}
        </select>
        <select value={filterClient} onChange={(e) => { setFilterClient(e.target.value); setPage(0); }} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
          <option value="">Todos los clientes</option>
          {clientsData?.items.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
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

      {/* Create/Edit Order Modal */}
      <FormModal open={showForm} title={editing ? 'Editar Orden' : 'Nueva Orden'} onClose={() => { setShowForm(false); setEditing(null); }}>
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
          <div>
            <label className="block text-sm font-medium text-gray-700">Equipamiento *</label>
            <select required value={formData.equipment_id} onChange={(e) => setFormData({ ...formData, equipment_id: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
              <option value="">Seleccionar equipamiento</option>
              {equipData?.items.map((eq) => (
                <option key={eq.id} value={eq.id}>{eq.brand} {eq.model} — {eq.serial_number}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Descripción</label>
            <textarea rows={3} value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Fecha de Servicio</label>
            <input type="date" value={formData.service_date} onChange={(e) => setFormData({ ...formData, service_date: e.target.value })} className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => { setShowForm(false); setEditing(null); }} className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">Cancelar</button>
            <button type="submit" disabled={createMutation.isPending || updateMutation.isPending} className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50">
              {createMutation.isPending || updateMutation.isPending ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </FormModal>

      {/* Parts Modal */}
      <FormModal open={!!viewingParts} title={`Partes — ${viewingParts?.order_number || ''}`} onClose={() => { setViewingParts(null); setPartForm(emptyPartForm); }}>
        {viewingParts && (
          <div className="space-y-4">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">Parte</th>
                    <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">Nº</th>
                    <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">Cant.</th>
                    <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">Costo</th>
                    <th className="px-3 py-2" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {viewingParts.parts.map((p) => (
                    <tr key={p.id}>
                      <td className="px-3 py-2 text-gray-900">{p.part_name}</td>
                      <td className="px-3 py-2 text-gray-600">{p.part_number || '-'}</td>
                      <td className="px-3 py-2 text-gray-600">{p.quantity}</td>
                      <td className="px-3 py-2 text-gray-600">{p.unit_cost != null ? `$${p.unit_cost}` : '-'}</td>
                      <td className="px-3 py-2 text-right">
                        <button onClick={() => removePartMutation.mutate({ orderId: viewingParts.id, partId: p.id })} className="text-red-600 hover:text-red-800">Eliminar</button>
                      </td>
                    </tr>
                  ))}
                  {viewingParts.parts.length === 0 && (
                    <tr><td colSpan={5} className="px-3 py-4 text-center text-gray-500">Sin partes registradas</td></tr>
                  )}
                </tbody>
              </table>
            </div>

            {(viewingParts.status === 'draft' || viewingParts.status === 'in_progress') && (
              <div className="border-t border-gray-200 pt-4">
                <h4 className="mb-2 text-sm font-medium text-gray-700">Agregar Parte</h4>
                <div className="grid gap-3 sm:grid-cols-4">
                  <input placeholder="Nombre *" value={partForm.part_name} onChange={(e) => setPartForm({ ...partForm, part_name: e.target.value })} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                  <input placeholder="Nº Parte" value={partForm.part_number} onChange={(e) => setPartForm({ ...partForm, part_number: e.target.value })} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                  <input type="number" min={1} value={partForm.quantity} onChange={(e) => setPartForm({ ...partForm, quantity: parseInt(e.target.value) || 1 })} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                  <button
                    onClick={() => partForm.part_name && addPartMutation.mutate({ orderId: viewingParts.id, data: partForm })}
                    disabled={!partForm.part_name || addPartMutation.isPending}
                    className="rounded-md bg-primary-600 px-3 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
                  >
                    Agregar
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </FormModal>

      <DeleteConfirm
        open={!!deleting}
        title="Eliminar Orden"
        message={`¿Estás seguro de eliminar la orden "${deleting?.order_number}"? Esta acción no se puede deshacer.`}
        onConfirm={() => deleting && deleteMutation.mutate(deleting.id)}
        onCancel={() => setDeleting(null)}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}
