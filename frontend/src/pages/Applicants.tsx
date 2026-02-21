import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Plus, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import { applicantsApi } from '@/services/api';
import type { Applicant } from '@/types';

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700',
  submitted: 'bg-blue-100 text-blue-700',
  reviewing: 'bg-yellow-100 text-yellow-700',
  approved: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  paid: 'bg-purple-100 text-purple-700',
};

export default function Applicants() {
  const [applicants, setApplicants] = useState<Applicant[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    ic_number: '',
    name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    monthly_income: 0,
    household_size: 1,
    occupation: '',
    employer: '',
  });

  useEffect(() => {
    loadApplicants();
  }, [page, status]);

  const loadApplicants = async () => {
    setLoading(true);
    try {
      const data = await applicantsApi.getAll({
        page,
        page_size: 10,
        search: search || undefined,
        status: status || undefined,
      });
      setApplicants(data.items);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to load applicants:', error);
      // Mock data
      setApplicants([
        { id: 1, ic_number: '880101012345', name: 'Ahmad bin Ali', status: 'approved', monthly_income: 400, household_size: 4, created_at: '2026-01-15', asnaf_category: 'fakir' },
        { id: 2, ic_number: '900202023456', name: 'Sarah bt Ahmad', status: 'reviewing', monthly_income: 800, household_size: 3, created_at: '2026-01-18', asnaf_category: 'miskin' },
        { id: 3, ic_number: '910303034567', name: 'Mohd Razak', status: 'submitted', monthly_income: 600, household_size: 5, created_at: '2026-01-20', asnaf_category: undefined },
      ]);
      setTotal(3);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadApplicants();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await applicantsApi.create(formData);
      setShowForm(false);
      setFormData({
        ic_number: '', name: '', email: '', phone: '', address: '',
        city: '', state: '', monthly_income: 0, household_size: 1, occupation: '', employer: '',
      });
      loadApplicants();
    } catch (error) {
      console.error('Failed to create applicant:', error);
      alert('Gagal mencipta permohonan');
    }
  };

  const totalPages = Math.ceil(total / 10);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Pengurusan Pemohon</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
        >
          <Plus className="w-4 h-4" />
          Permohonan Baru
        </button>
      </div>

      {/* New applicant form */}
      {showForm && (
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Permohonan Baru</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">No. IC</label>
              <input
                type="text"
                value={formData.ic_number}
                onChange={(e) => setFormData({ ...formData, ic_number: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nama Penuh</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">No. Telefon</label>
              <input
                type="text"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Alamat</label>
              <textarea
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
                rows={2}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Bandar</label>
              <input
                type="text"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Negeri</label>
              <input
                type="text"
                value={formData.state}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Pendapatan Bulanan (RM)</label>
              <input
                type="number"
                value={formData.monthly_income}
                onChange={(e) => setFormData({ ...formData, monthly_income: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Saiz Isi Rumah</label>
              <input
                type="number"
                value={formData.household_size}
                onChange={(e) => setFormData({ ...formData, household_size: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Pekerjaan</label>
              <input
                type="text"
                value={formData.occupation}
                onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Majikan</label>
              <input
                type="text"
                value={formData.employer}
                onChange={(e) => setFormData({ ...formData, employer: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div className="md:col-span-2 flex gap-2">
              <button type="submit" className="px-4 py-2 bg-primary text-white rounded-lg">
                Hantar
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 border rounded-lg"
              >
                Batal
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 shadow-sm border">
        <form onSubmit={handleSearch} className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Cari nama atau IC..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg"
              />
            </div>
          </div>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="">Semua Status</option>
            <option value="draft">Draf</option>
            <option value="submitted">Dihantar</option>
            <option value="reviewing">Semakan</option>
            <option value="approved">Diluluskan</option>
            <option value="rejected">Ditolak</option>
            <option value="paid">Dibayar</option>
          </select>
          <button type="submit" className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200">
            <Filter className="w-4 h-4" />
          </button>
        </form>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">No. IC</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Nama</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Status</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Pendapatan</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Asnaf</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Tarikh</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Tindakan</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto"></div>
                  </td>
                </tr>
              ) : applicants.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                    Tiada permohonan dijumpai
                  </td>
                </tr>
              ) : (
                applicants.map((applicant) => (
                  <tr key={applicant.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">{applicant.ic_number}</td>
                    <td className="px-4 py-3 text-sm font-medium">{applicant.name}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[applicant.status] || 'bg-gray-100'}`}>
                        {applicant.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">RM{applicant.monthly_income.toFixed(2)}</td>
                    <td className="px-4 py-3 text-sm">{applicant.asnaf_category || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {new Date(applicant.created_at).toLocaleDateString('ms-MY')}
                    </td>
                    <td className="px-4 py-3">
                      <Link
                        to={`/applicants/${applicant.id}`}
                        className="text-primary hover:underline text-sm"
                      >
                        Lihat
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t">
            <p className="text-sm text-gray-500">
              Showing {(page - 1) * 10 + 1} to {Math.min(page * 10, total)} of {total}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="p-2 rounded-lg border disabled:opacity-50"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}
                className="p-2 rounded-lg border disabled:opacity-50"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}