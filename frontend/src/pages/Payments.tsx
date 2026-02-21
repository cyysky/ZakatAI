import { useEffect, useState } from 'react';
import { Search, ChevronLeft, ChevronRight, DollarSign, CheckCircle, XCircle, Clock } from 'lucide-react';
import { paymentsApi } from '@/services/api';
import type { Payment } from '@/types';

const statusConfig: Record<string, { color: string; bg: string; icon: any }> = {
  pending: { color: 'text-yellow-700', bg: 'bg-yellow-100', icon: Clock },
  processing: { color: 'text-blue-700', bg: 'bg-blue-100', icon: Clock },
  completed: { color: 'text-green-700', bg: 'bg-green-100', icon: CheckCircle },
  failed: { color: 'text-red-700', bg: 'bg-red-100', icon: XCircle },
  cancelled: { color: 'text-gray-700', bg: 'bg-gray-100', icon: XCircle },
};

export default function Payments() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    loadPayments();
    loadSummary();
  }, [page, status]);

  const loadPayments = async () => {
    setLoading(true);
    try {
      const data = await paymentsApi.getAll({ page, page_size: 10, status: status || undefined });
      setPayments(data);
      setTotal(data.length);
    } catch (error) {
      console.error('Failed to load payments:', error);
      setPayments([
        { id: 1, applicant_id: 1, payment_reference: 'ZKT-20260115-001', amount: 500, status: 'completed', created_at: '2026-01-15', is_anomaly: false },
        { id: 2, applicant_id: 2, payment_reference: 'ZKT-20260118-002', amount: 300, status: 'pending', created_at: '2026-01-18', is_anomaly: false },
        { id: 3, applicant_id: 3, payment_reference: 'ZKT-20260120-003', amount: 1000, status: 'processing', created_at: '2026-01-20', is_anomaly: true, anomaly_reason: 'Amlout unusual' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    try {
      const data = await paymentsApi.getSummary();
      setSummary(data);
    } catch (error) {
      setSummary({
        total_payments: 150,
        total_amount: 75000,
        by_status: [
          { status: 'completed', count: 120, amount: 60000 },
          { status: 'pending', count: 20, amount: 10000 },
          { status: 'failed', count: 10, amount: 5000 },
        ],
        anomaly_count: 3,
      });
    }
  };

  const handleApprove = async (id: number, approved: boolean) => {
    try {
      await paymentsApi.approve(id, approved);
      loadPayments();
    } catch (error) {
      console.error('Approval failed:', error);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Pengurusan Pembayaran</h1>

      {/* Summary cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Jumlah Pembayaran</p>
                <p className="text-2xl font-bold">{summary.total_payments}</p>
              </div>
              <DollarSign className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Jumlah Dibayar</p>
                <p className="text-2xl font-bold text-green-600">RM{summary.total_amount?.toLocaleString() || 0}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Tertunda</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {summary.by_status?.find((s: any) => s.status === 'pending')?.count || 0}
                </p>
              </div>
              <Clock className="w-8 h-8 text-yellow-600" />
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Anomali</p>
                <p className="text-2xl font-bold text-red-600">{summary.anomaly_count || 0}</p>
              </div>
              <XCircle className="w-8 h-8 text-red-600" />
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 shadow-sm border">
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="">Semua Status</option>
          <option value="pending">Tertunda</option>
          <option value="processing">Sedang Diproses</option>
          <option value="completed">Siap</option>
          <option value="failed">Gagal</option>
          <option value="cancelled">Dibatalkan</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Rujukan</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">ID Pemohon</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Amaun</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Status</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Tarikh</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Tindakan</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto"></div>
                  </td>
                </tr>
              ) : payments.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                    Tiada pembayaran dijumpai
                  </td>
                </tr>
              ) : (
                payments.map((payment) => {
                  const config = statusConfig[payment.status] || statusConfig.pending;
                  const Icon = config.icon;

                  return (
                    <tr key={payment.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-mono">{payment.payment_reference}</td>
                      <td className="px-4 py-3 text-sm">{payment.applicant_id}</td>
                      <td className="px-4 py-3 text-sm font-medium">RM{payment.amount.toFixed(2)}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${config.bg} ${config.color}`}>
                          <Icon className="w-3 h-3" />
                          {payment.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {new Date(payment.created_at).toLocaleDateString('ms-MY')}
                      </td>
                      <td className="px-4 py-3">
                        {payment.status === 'pending' && (
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleApprove(payment.id, true)}
                              className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200"
                            >
                              Lulus
                            </button>
                            <button
                              onClick={() => handleApprove(payment.id, false)}
                              className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                            >
                              Tolak
                            </button>
                          </div>
                        )}
                        {payment.is_anomaly && (
                          <span className="text-xs text-red-600">Anomali dikesan</span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}