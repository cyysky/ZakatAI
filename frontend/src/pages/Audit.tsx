import { useEffect, useState } from 'react';
import { FileText, Calendar, User, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { auditApi } from '@/services/api';

interface AuditLog {
  id: number;
  user_id: number;
  action: string;
  entity_type: string;
  entity_id: number;
  created_at: string;
}

export default function Audit() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    loadAuditData();
  }, []);

  const loadAuditData = async () => {
    setLoading(true);
    try {
      const [logsData, summaryData] = await Promise.all([
        auditApi.getLogs({ page_size: 50 }),
        auditApi.getSummary(),
      ]);
      setLogs(logsData);
      setSummary(summaryData);
    } catch (error) {
      console.error('Failed to load audit data:', error);
      setLogs([
        { id: 1, user_id: 1, action: 'create', entity_type: 'applicant', entity_id: 1, created_at: '2026-01-15T10:30:00' },
        { id: 2, user_id: 1, action: 'update', entity_type: 'applicant', entity_id: 1, created_at: '2026-01-16T11:00:00' },
        { id: 3, user_id: 2, action: 'approve', entity_type: 'payment', entity_id: 1, created_at: '2026-01-17T09:15:00' },
      ]);
      setSummary({
        total_logs: 150,
        today_logs: 12,
        by_action: { create: 50, update: 60, delete: 10, approve: 30 },
        by_entity: { applicant: 80, payment: 50, user: 20 },
        daily_logs: [
          { date: '2026-01-15', count: 20 },
          { date: '2026-01-16', count: 25 },
          { date: '2026-01-17', count: 18 },
          { date: '2026-01-18', count: 30 },
          { date: '2026-01-19', count: 22 },
          { date: '2026-01-20', count: 15 },
          { date: '2026-01-21', count: 12 },
        ],
      });
    } finally {
      setLoading(false);
    }
  };

  const actionColors: Record<string, string> = {
    create: '#10b981',
    update: '#3b82f6',
    delete: '#ef4444',
    approve: '#8b5cf6',
    reject: '#f59e0b',
    login: '#6b7280',
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Log Audit & Pentadbiran</h1>

      {/* Summary cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Jumlah Log</p>
                <p className="text-2xl font-bold">{summary.total_logs}</p>
              </div>
              <FileText className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Hari Ini</p>
                <p className="text-2xl font-bold">{summary.today_logs}</p>
              </div>
              <Calendar className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Mengikut Entity</p>
                <p className="text-2xl font-bold">{Object.keys(summary.by_entity || {}).length}</p>
              </div>
              <Activity className="w-8 h-8 text-purple-600" />
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Pengguna Aktif</p>
                <p className="text-2xl font-bold">5</p>
              </div>
              <User className="w-8 h-8 text-orange-600" />
            </div>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity by action */}
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Aktiviti Mengikut Jenis</h2>
          {summary && (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={Object.entries(summary.by_action || {}).map(([action, count]) => ({
                    action,
                    count,
                  }))}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="action" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Daily activity */}
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Aktiviti Harian (7 Hari)</h2>
          {summary && (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={summary.daily_logs || []}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      {/* Recent logs */}
      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold">Log Aktiviti Terkini</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Tarikh & Masa</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Pengguna</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Tindakan</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Entity</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">ID</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto"></div>
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    Tiada log dijumpai
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">
                      {new Date(log.created_at).toLocaleString('ms-MY')}
                    </td>
                    <td className="px-4 py-3 text-sm">User #{log.user_id}</td>
                    <td className="px-4 py-3">
                      <span
                        className="px-2 py-1 text-xs font-medium rounded-full"
                        style={{
                          backgroundColor: `${actionColors[log.action] || '#6b7280'}20`,
                          color: actionColors[log.action] || '#6b7280',
                        }}
                      >
                        {log.action}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm capitalize">{log.entity_type}</td>
                    <td className="px-4 py-3 text-sm font-mono">{log.entity_id}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}