import { useState, useEffect, type FormEvent } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ordersApi, clientsApi, equipmentApi, empleadosApi, departamentosApi, pdfApi } from '../api/endpoints';
import type { OrdenServicio, TipoVisita, CondicionEquipoOrden } from '../types';
import { DataTable } from '../components/DataTable';
import { FormModal } from '../components/FormModal';
import { DeleteConfirm } from '../components/DeleteConfirm';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useAuth } from '../hooks/useAuth';

interface OrderForm {
  id_cliente: number | '';
  id_equipo: number | '';
  id_departamento: number | '';
  solicitado_por: string;
  tipo_visita: TipoVisita;
  condicion_equipo: CondicionEquipoOrden;
  configuracion_equipo: string;
  accesorios: string;
  fecha_realizacion: string;
  fecha_finalizacion: string;
  falla_detectada: string;
  tarea_realizada: string;
  horas_trabajo: string;
  cantidad_operarios: number;
  id_empleados: number[];
  kilometros: string;
  viaticos: string;
}

const emptyForm: OrderForm = {
  id_cliente: '',
  id_equipo: '',
  id_departamento: '',
  solicitado_por: '',
  tipo_visita: 'normal',
  condicion_equipo: 'usado',
  configuracion_equipo: '',
  accesorios: '',
  fecha_realizacion: '',
  fecha_finalizacion: '',
  falla_detectada: '',
  tarea_realizada: '',
  horas_trabajo: '',
  cantidad_operarios: 1,
  id_empleados: [],
  kilometros: '',
  viaticos: '',
};

export function ServiceOrders() {
  const { isAdmin } = useAuth();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<OrdenServicio | null>(null);
  const [deleting, setDeleting] = useState<OrdenServicio | null>(null);
  const [formData, setFormData] = useState<OrderForm>(emptyForm);
  const [filterClient, setFilterClient] = useState<number | ''>('');
  const [filterClientType, setFilterClientType] = useState('');
  const [error, setError] = useState('');
  const pageSize = 20;

  const { data, isLoading } = useQuery({
    queryKey: ['orders', page, filterClient],
    queryFn: () =>
      ordersApi.list({
        skip: page * pageSize,
        limit: pageSize,
        ...(filterClient !== '' ? { id_cliente: filterClient } : {}),
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

  const { data: empleadosData } = useQuery({
    queryKey: ['empleados-list'],
    queryFn: () => empleadosApi.getAll(),
  });

  const { data: departamentosData } = useQuery({
    queryKey: ['departamentos-list', formData.id_cliente],
    queryFn: () => departamentosApi.getByCliente(formData.id_cliente as number),
    enabled: formData.id_cliente !== '',
  });

  useEffect(() => {
    if (formData.id_cliente !== '') {
      setFormData((prev) => ({ ...prev, id_departamento: '', id_equipo: '' }));
    }
  }, [formData.id_cliente]);

  useEffect(() => {
    setFormData((prev) => ({ ...prev, id_empleados: prev.id_empleados.slice(0, prev.cantidad_operarios) }));
  }, [formData.cantidad_operarios]);

  const filteredClients = filterClientType
    ? clientsData?.items.filter((c) => c.tipo_cliente === filterClientType) || []
    : clientsData?.items || [];

  const filteredEquipos = equipData?.items.filter(
    (eq) => formData.id_cliente === '' || eq.id_cliente === formData.id_cliente
  );

  const selectedEquipo = equipData?.items.find((eq) => eq.id_equipos === formData.id_equipo);
  const isRayosX = selectedEquipo?.id_tipo_equipos === 4;

  const getAvailableEmpleados = (currentIndex: number) => {
    const selectedOthers = formData.id_empleados.filter((_, i) => i !== currentIndex);
    return empleadosData?.items.filter((em) => !selectedOthers.includes(em.id_empleado)) || [];
  };

  const createMutation = useMutation({
    mutationFn: (d: OrderForm) =>
      ordersApi.create({
        id_cliente: d.id_cliente as number,
        id_equipo: d.id_equipo as number,
        id_empleado: d.id_empleados[0] || 0,
        id_departamento: d.id_departamento ? Number(d.id_departamento) : undefined,
        solicitado_por: d.solicitado_por,
        tipo_visita: d.tipo_visita,
        condicion_equipo: d.condicion_equipo,
        configuracion_equipo: d.configuracion_equipo || undefined,
        accesorios: d.accesorios || undefined,
        fecha_realizacion: d.fecha_realizacion,
        fecha_finalizacion: d.fecha_finalizacion || undefined,
        falla_detectada: d.falla_detectada,
        tarea_realizada: d.tarea_realizada || undefined,
        horas_trabajo: d.horas_trabajo ? parseFloat(d.horas_trabajo) : undefined,
        empleados_adicionales: d.id_empleados.length > 1 ? d.id_empleados.slice(1).join(',') : undefined,
        kilometros: d.kilometros ? parseFloat(d.kilometros) : undefined,
        viaticos: d.viaticos ? parseFloat(d.viaticos) : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      setShowForm(false);
      setFormData(emptyForm);
    },
    onError: (err: Error) => setError(err.message),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data: d }: { id: number; data: OrderForm }) =>
      ordersApi.update(id, {
        id_cliente: d.id_cliente as number,
        id_equipo: d.id_equipo as number,
        id_empleado: d.id_empleados[0] || 0,
        id_departamento: d.id_departamento ? Number(d.id_departamento) : undefined,
        solicitado_por: d.solicitado_por,
        tipo_visita: d.tipo_visita,
        condicion_equipo: d.condicion_equipo,
        configuracion_equipo: d.configuracion_equipo || undefined,
        accesorios: d.accesorios || undefined,
        fecha_realizacion: d.fecha_realizacion,
        fecha_finalizacion: d.fecha_finalizacion || undefined,
        falla_detectada: d.falla_detectada,
        tarea_realizada: d.tarea_realizada || undefined,
        horas_trabajo: d.horas_trabajo ? parseFloat(d.horas_trabajo) : undefined,
        empleados_adicionales: d.id_empleados.length > 1 ? d.id_empleados.slice(1).join(',') : undefined,
        kilometros: d.kilometros ? parseFloat(d.kilometros) : undefined,
        viaticos: d.viaticos ? parseFloat(d.viaticos) : undefined,
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
    mutationFn: (id: number) => ordersApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      setDeleting(null);
    },
  });

  const downloadPdf = async (orderId: number) => {
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
      updateMutation.mutate({ id: editing.id_orden, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const openCreate = () => {
    setEditing(null);
    setFormData(emptyForm);
    setShowForm(true);
  };

  const openEdit = (order: OrdenServicio) => {
    const allEmpleados = [order.id_empleado];
    if (order.empleados_adicionales) {
      order.empleados_adicionales.split(',').forEach((id) => {
        const parsed = parseInt(id.trim(), 10);
        if (!isNaN(parsed)) allEmpleados.push(parsed);
      });
    }
    setEditing(order);
    setFormData({
      id_cliente: order.id_cliente,
      id_equipo: order.id_equipo,
      id_departamento: order.id_departamento ?? '',
      solicitado_por: order.solicitado_por,
      tipo_visita: order.tipo_visita,
      condicion_equipo: order.condicion_equipo,
      accesorios: order.accesorios || '',
      fecha_realizacion: order.fecha_realizacion,
      fecha_finalizacion: order.fecha_finalizacion || '',
      falla_detectada: order.falla_detectada || '',
      tarea_realizada: order.tarea_realizada || '',
      horas_trabajo: order.horas_trabajo?.toString() || '',
      cantidad_operarios: allEmpleados.length,
      id_empleados: allEmpleados,
      kilometros: order.kilometros?.toString() || '',
      viaticos: order.viaticos?.toString() || '',
      configuracion_equipo: order.configuracion_equipo || '',
    });
    setShowForm(true);
  };

  const getClientName = (id: number) => clientsData?.items.find((c) => c.id_cliente === id)?.nombre || id.toString();
  const getEquipoInfo = (id: number) => {
    const eq = equipData?.items.find((e) => e.id_equipos === id);
    return eq ? `${eq.modelo}${eq.numero_serie ? ' — ' + eq.numero_serie : ''}` : id.toString();
  };
  const getEmpleadoName = (id: number) => empleadosData?.items.find((e) => e.id_empleado === id)?.nombre || id.toString();

  const inputClass = 'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500';

  const columns = [
    { key: 'numero_orden', header: 'OS' },
    { key: 'id_cliente', header: 'Cliente', render: (item: unknown) => getClientName((item as OrdenServicio).id_cliente) },
    { key: 'id_equipo', header: 'Equipo', render: (item: unknown) => getEquipoInfo((item as OrdenServicio).id_equipo) },
    { key: 'id_empleado', header: 'Técnico', render: (item: unknown) => getEmpleadoName((item as OrdenServicio).id_empleado) },
    { key: 'fecha_realizacion', header: 'Fecha', render: (item: unknown) => (item as OrdenServicio).fecha_realizacion || '-' },
    { key: 'tarea_realizada', header: 'Tarea', render: (item: unknown) => {
      const t = (item as OrdenServicio).tarea_realizada;
      if (!t) return '-';
      return t.length > 40 ? t.substring(0, 40) + '…' : t;
    }},
    {
      key: 'actions',
      header: 'Acciones',
      className: 'w-44',
      render: (item: unknown) => {
        const o = item as OrdenServicio;
        return (
          <div className="flex flex-wrap gap-1">
            <button onClick={(ev) => { ev.stopPropagation(); openEdit(o); }} className="text-sm text-primary-600 hover:text-primary-800">Editar</button>
            <button onClick={(ev) => { ev.stopPropagation(); downloadPdf(o.id_orden); }} className="text-sm text-green-600 hover:text-green-800">PDF</button>
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
        <select value={filterClient} onChange={(e) => { setFilterClient(e.target.value ? Number(e.target.value) : ''); setPage(0); }} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
          <option value="">Todos los clientes</option>
          {filteredClients.map((c) => (
            <option key={c.id_cliente} value={c.id_cliente}>{c.nombre}</option>
          ))}
        </select>
        <select value={filterClientType} onChange={(e) => { setFilterClientType(e.target.value); setFilterClient(''); setPage(0); }} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
          <option value="">Todos los tipos</option>
          <option value="juridica">Persona Jurídica</option>
          <option value="fisica">Persona Física</option>
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

      <FormModal open={showForm} title={editing ? 'Editar Orden' : 'Nueva Orden'} onClose={() => { setShowForm(false); setEditing(null); }}>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}

          {/* 1. Cliente */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Cliente *</label>
            <select required value={formData.id_cliente} onChange={(e) => setFormData({ ...formData, id_cliente: e.target.value ? Number(e.target.value) : '' })} className={inputClass}>
              <option value="">Seleccionar cliente</option>
              <optgroup label="Persona Jurídica">
                {clientsData?.items.filter((c) => c.tipo_cliente === 'juridica').map((c) => (
                  <option key={c.id_cliente} value={c.id_cliente}>{c.nombre}</option>
                ))}
              </optgroup>
              <optgroup label="Persona Física">
                {clientsData?.items.filter((c) => c.tipo_cliente === 'fisica').map((c) => (
                  <option key={c.id_cliente} value={c.id_cliente}>{c.nombre}</option>
                ))}
              </optgroup>
            </select>
          </div>

          {/* 2. Equipo */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Equipo *</label>
            <select required value={formData.id_equipo} onChange={(e) => setFormData({ ...formData, id_equipo: e.target.value ? Number(e.target.value) : '' })} className={inputClass}>
              <option value="">Seleccionar equipo</option>
              {filteredEquipos?.map((eq) => (
                <option key={eq.id_equipos} value={eq.id_equipos}>{eq.modelo}{eq.numero_serie ? ' — ' + eq.numero_serie : ''}</option>
              ))}
            </select>
          </div>

          {/* 3. Solicitado por */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Solicitado por *</label>
            <input required value={formData.solicitado_por} onChange={(e) => setFormData({ ...formData, solicitado_por: e.target.value })} className={inputClass} />
          </div>

          {/* 4. Puesto o Departamento del solicitante (optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Puesto o Departamento del solicitante</label>
            <select value={formData.id_departamento} onChange={(e) => setFormData({ ...formData, id_departamento: e.target.value ? Number(e.target.value) : '' })} className={inputClass} disabled={formData.id_cliente === ''}>
              <option value="">Seleccionar departamento</option>
              {departamentosData?.items.map((d) => (
                <option key={d.id_departamento} value={d.id_departamento}>{d.nombre}</option>
              ))}
            </select>
          </div>

          {/* 5. Cantidad de Operarios */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Cantidad de Operarios *</label>
            <input type="number" required min={1} max={5} value={formData.cantidad_operarios} onChange={(e) => setFormData({ ...formData, cantidad_operarios: Math.max(1, Math.min(5, Number(e.target.value) || 1)) })} className={inputClass} />
          </div>

          {/* 6-7. Técnicos dinámicos */}
          {Array.from({ length: formData.cantidad_operarios }).map((_, i) => (
            <div key={i}>
              <label className="block text-sm font-medium text-gray-700">Técnico {i + 1} *</label>
              <select
                required
                value={formData.id_empleados[i] || ''}
                onChange={(e) => {
                  const newSelected = [...formData.id_empleados];
                  newSelected[i] = e.target.value ? Number(e.target.value) : 0;
                  setFormData({ ...formData, id_empleados: newSelected });
                }}
                className={inputClass}
              >
                <option value="">Seleccionar técnico</option>
                {getAvailableEmpleados(i).map((em) => (
                  <option key={em.id_empleado} value={em.id_empleado}>{em.nombre}</option>
                ))}
              </select>
            </div>
          ))}

          {/* 8. Tipo de Visita */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Tipo de Visita *</label>
            <select required value={formData.tipo_visita} onChange={(e) => setFormData({ ...formData, tipo_visita: e.target.value as TipoVisita })} className={inputClass}>
              <option value="normal">Normal</option>
              <option value="por contrato">Por Contrato</option>
              <option value="por garantía">Por Garantía</option>
            </select>
          </div>

          {/* 9. Condición Equipo */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Condición Equipo *</label>
            <select required value={formData.condicion_equipo} onChange={(e) => setFormData({ ...formData, condicion_equipo: e.target.value as CondicionEquipoOrden })} className={inputClass}>
              <option value="nuevo">Nuevo</option>
              <option value="usado">Usado</option>
              <option value="otro">Otro</option>
            </select>
          </div>

          {/* 9b. Configuración del equipo (solo Rayos X) */}
          {isRayosX && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Configuración del Equipo</label>
              <select value={formData.configuracion_equipo} onChange={(e) => setFormData({ ...formData, configuracion_equipo: e.target.value })} className={inputClass}>
                <option value="">Seleccionar configuración</option>
                <option value="Rodante">Rodante</option>
                <option value="Rodante c/Seriografo">Rodante c/Seriografo</option>
                <option value="Fijo">Fijo</option>
              </select>
            </div>
          )}

          {/* 10. Falla Detectada */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Falla Detectada *</label>
            <textarea rows={3} required value={formData.falla_detectada} onChange={(e) => setFormData({ ...formData, falla_detectada: e.target.value })} className={inputClass} />
          </div>

          {/* 11. Tarea Realizada (optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Tarea Realizada</label>
            <textarea rows={3} value={formData.tarea_realizada} onChange={(e) => setFormData({ ...formData, tarea_realizada: e.target.value })} className={inputClass} />
          </div>

          {/* 12-13. Fechas */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Fecha Realización *</label>
              <input type="date" required value={formData.fecha_realizacion} onChange={(e) => setFormData({ ...formData, fecha_realizacion: e.target.value })} className={inputClass} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Fecha Finalización</label>
              <input type="date" value={formData.fecha_finalizacion} onChange={(e) => setFormData({ ...formData, fecha_finalizacion: e.target.value })} className={inputClass} />
            </div>
          </div>

          {/* 14. Horas de Trabajo */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Horas de Trabajo</label>
            <input type="number" step="0.5" min="0" value={formData.horas_trabajo} onChange={(e) => setFormData({ ...formData, horas_trabajo: e.target.value })} className={inputClass} />
          </div>

          {/* 15. Accesorios */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Accesorios</label>
            <input value={formData.accesorios} onChange={(e) => setFormData({ ...formData, accesorios: e.target.value })} className={inputClass} />
          </div>

          {/* 16-17. Kilómetros y Viáticos */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Kilómetros Recorridos</label>
              <input type="number" step="0.01" min="0" value={formData.kilometros} onChange={(e) => setFormData({ ...formData, kilometros: e.target.value })} className={inputClass} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Viáticos</label>
              <input type="number" step="0.01" min="0" value={formData.viaticos} onChange={(e) => setFormData({ ...formData, viaticos: e.target.value })} className={inputClass} />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => { setShowForm(false); setEditing(null); }} className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">Cancelar</button>
            <button type="submit" disabled={createMutation.isPending || updateMutation.isPending} className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50">
              {createMutation.isPending || updateMutation.isPending ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </FormModal>

      <DeleteConfirm
        open={!!deleting}
        title="Eliminar Orden"
        message={`¿Estás seguro de eliminar la orden "${deleting?.numero_orden}"? Esta acción no se puede deshacer.`}
        onConfirm={() => deleting && deleteMutation.mutate(deleting.id_orden)}
        onCancel={() => setDeleting(null)}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}
