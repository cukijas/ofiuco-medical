import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { publicApi } from '../api/endpoints';
import type { Equipment, Attachment } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';

export function PublicEquipment() {
  const { qrId } = useParams<{ qrId: string }>();
  const [equipment, setEquipment] = useState<Equipment | null>(null);
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!qrId) return;

    publicApi
      .getEquipment(qrId)
      .then((eq) => {
        setEquipment(eq);
        return publicApi.getAttachments(eq.id_equipos);
      })
      .then((att) => setAttachments(att.items))
      .catch((err) => setError(err.message || 'Equipo no encontrado'))
      .finally(() => setLoading(false));
  }, [qrId]);

  if (loading) return <LoadingSpinner />;
  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">Ofiuco Medical</h1>
          <p className="mt-2 text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white px-4 py-4">
        <div className="mx-auto max-w-2xl">
          <h1 className="text-lg font-bold text-primary-700">Ofiuco Medical</h1>
          <p className="text-xs text-gray-500">Información del Equipamiento</p>
        </div>
      </header>

      <main className="mx-auto max-w-2xl space-y-6 p-4">
        {equipment && (
          <section className="rounded-lg border border-gray-200 bg-white p-4">
            <h2 className="text-lg font-semibold text-gray-900">Información del Equipo</h2>
            <dl className="mt-3 grid gap-3 sm:grid-cols-2">
              <div>
                <dt className="text-xs font-medium text-gray-500">Marca / Modelo</dt>
                <dd className="text-sm text-gray-900">{equipment.modelo}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500">Número de Serie</dt>
                <dd className="text-sm text-gray-900">{equipment.numero_serie}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500">Condición</dt>
                <dd className="text-sm text-gray-900 capitalize">{equipment.condicion}</dd>
              </div>
              {equipment.descripcion && (
                <div className="sm:col-span-2">
                  <dt className="text-xs font-medium text-gray-500">Descripción</dt>
                  <dd className="text-sm text-gray-900">{equipment.descripcion}</dd>
                </div>
              )}
              {equipment.accesorios && (
                <div className="sm:col-span-2">
                  <dt className="text-xs font-medium text-gray-500">Accesorios</dt>
                  <dd className="text-sm text-gray-900">{equipment.accesorios}</dd>
                </div>
              )}
              <div>
                <dt className="text-xs font-medium text-gray-500">Fecha de Registro</dt>
                <dd className="text-sm text-gray-900">{new Date(equipment.created_at).toLocaleDateString('es-AR')}</dd>
              </div>
            </dl>
          </section>
        )}

        <section className="rounded-lg border border-gray-200 bg-white p-4">
          <h2 className="text-lg font-semibold text-gray-900">Documentos y Archivos</h2>
          {attachments.length === 0 ? (
            <p className="mt-3 text-sm text-gray-500">No hay documentos disponibles.</p>
          ) : (
            <ul className="mt-3 divide-y divide-gray-100">
              {attachments.map((att) => (
                <li key={att.id} className="flex items-center justify-between py-2">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{att.file_name}</p>
                    <p className="text-xs text-gray-500 capitalize">{att.file_type}</p>
                  </div>
                  <a
                    href={`/public/equipment/attachments/${att.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary-600 hover:text-primary-800"
                  >
                    Descargar
                  </a>
                </li>
              ))}
            </ul>
          )}
        </section>

        <footer className="text-center text-xs text-gray-400">
          Ofiuco Medical — Servicios de Ingeniería Biomédica
        </footer>
      </main>
    </div>
  );
}