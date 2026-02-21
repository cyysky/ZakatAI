import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, FileCheck, Clock, AlertTriangle, TrendingUp, DollarSign } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { dashboardApi } from '@/services/api';
import type { DashboardStats, CriticalCase } from '@/types';

const statusColors: Record<string, string> = {
  draft: '#6b7280',
  submitted: '#3b82f6',
  reviewing: '#f59e0b',
  approved: '#10b981',
  rejected: '#ef4444',
  paid: '#8b5cf6',
};

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [criticalCases, setCriticalCases] = useState<CriticalCase[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [statsData, casesData] = await Promise.all([
        dashboardApi.getStats(),
        dashboardApi.getCriticalCases(),
      ]);
      setStats(statsData);
      setCriticalCases(casesData);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      // Use mock data on error
      setStats({
        total_applicants: 800,
        by_status: {
          draft: 50,
          submitted: 150,
          reviewing: 100,
          approved: 350,
          rejected: 100,
          paid: 50,
        },
        recent_applications: 120,
        pending_payments: 25,
        avg_processing_days: 14,
        fraud_alerts: 5,
      });
      setCriticalCases([
        {
          type: 'long_pending',
          severity: 'tinggi',
          applicant_id: 1,
          applicant_name: 'Ahmad bin Ali',
          ic_number: '880101012345',
          days_pending: 45,
          description: 'Permohonan masih belum selesai sejak 45 hari',
          recommended_action: 'Semak dan proses dengan segera',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  const statusData = stats ? Object.entries(stats.by_status).map(([status, count]) => ({
    name: status.charAt(0).toUpperCase() + status.slice(1),
    value: count,
    color: statusColors[status] || '#6b7280',
  })) : [];

  const mockTrendData = [
    { month: 'Ogos', applications: 120 },
    { month: 'Sept', applications: 145 },
    { month: 'Okt', applications: 130 },
    { month: 'Nov', applications: 165 },
    { month: 'Dis', applications: 180 },
    { month: 'Jan', applications: 175 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard Pengurusan Zakat</h1>
        <p className="text-sm text-gray-500">
          Kemaskini terakhir: {new Date().toLocaleDateString('ms-MY')}
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Jumlah Permohonan</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.total_applicants || 0}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Permohonan Baru (7 hari)</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.recent_applications || 0}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Pembayaran Tertunda</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.pending_payments || 0}</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Amaran Penipuan</p>
              <p className="text-2xl font-bold text-red-600">{stats?.fraud_alerts || 0}</p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status distribution */}
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Taburan Status</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap gap-3 mt-4">
            {statusData.map((item) => (
              <div key={item.name} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-sm text-gray-600">{item.name}: {item.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Monthly trend */}
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Trend Permohonan Bulanan</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockTrendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="applications" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Critical cases */}
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-yellow-500" />
          Kes Kritikal Memerlukan Tindakan
        </h2>
        {criticalCases.length === 0 ? (
          <p className="text-gray-500 text-center py-4">Tiada kes kritikal</p>
        ) : (
          <div className="space-y-3">
            {criticalCases.slice(0, 5).map((caseItem, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-l-4 ${
                  caseItem.severity === 'tinggi'
                    ? 'bg-red-50 border-red-500'
                    : caseItem.severity === 'sederhana'
                    ? 'bg-yellow-50 border-yellow-500'
                    : 'bg-blue-50 border-blue-500'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{caseItem.applicant_name}</p>
                    <p className="text-sm text-gray-600">IC: {caseItem.ic_number}</p>
                    <p className="text-sm mt-1">{caseItem.description}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    caseItem.severity === 'tinggi'
                      ? 'bg-red-100 text-red-700'
                      : caseItem.severity === 'sederhana'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-blue-100 text-blue-700'
                  }`}>
                    {caseItem.severity.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  <strong>Tindakan:</strong> {caseItem.recommended_action}
                </p>
                <Link
                  to={`/applicants/${caseItem.applicant_id}`}
                  className="text-sm text-primary hover:underline mt-2 inline-block"
                >
                  Lihat详情 &rarr;
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}