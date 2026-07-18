import type { StatusEnum } from '../types';

const statusConfig: Record<StatusEnum, { label: string; className: string }> = {
  draft: { label: 'Borrador', className: 'bg-gray-100 text-gray-800' },
  in_progress: { label: 'En Progreso', className: 'bg-blue-100 text-blue-800' },
  completed: { label: 'Completado', className: 'bg-green-100 text-green-800' },
  delivered: { label: 'Entregado', className: 'bg-purple-100 text-purple-800' },
};

export function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status as StatusEnum] || {
    label: status,
    className: 'bg-gray-100 text-gray-800',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${config.className}`}
    >
      {config.label}
    </span>
  );
}
