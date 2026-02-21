import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle, XCircle, AlertTriangle, FileText, Upload } from 'lucide-react';
import { applicantsApi } from '@/services/api';
import type { Applicant } from '@/types';

export default function ApplicantDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [applicant, setApplicant] = useState<Applicant | null>(null);
  const [loading, setLoading] = useState(true);
  const [assessing, setAssessing] = useState(false);

  useEffect(() => {
    if (id) loadApplicant(parseInt(id));
  }, [id]);

  const loadApplicant = async (applicantId: number) => {
    setLoading(true);
    try {
      const data = await applicantsApi.getById(applicantId);
      setApplicant(data);
    } catch (error) {
      console.error('Failed to load applicant:', error);
      // Mock data
      setApplicant({
        id: applicantId,
        ic_number: '880101012345',
        name: 'Ahmad bin Ali',
        email: 'ahmad@example.com',
        phone: '0123456789',
        address: 'No. 123, Jalan Ampang',
        city: 'Kuala Lumpur',
        state: 'WP Kuala Lumpur',
        monthly_income: 400,
        household_size: 4,
        occupation: 'Bekerja sendiri',
        eligibility_score: 0.85,
        fraud_risk_score: 0.15,
        is_fraud_detected: false,
        status: 'reviewing',
        asnaf_category: 'fakir',
        created_at: '2026-01-15',
        updated_at: '2026-01-18',
        documents: [],
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAssess = async () => {
    if (!id) return;
    setAssessing(true);
    try {
      const result = await applicantsApi.assess(parseInt(id));
      setApplicant((prev) => prev ? { ...prev, ...result } : null);
    } catch (error) {
      console.error('Assessment failed:', error);
    } finally {
      setAssessing(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!id) return;
    try {
      await applicantsApi.updateStatus(parseInt(id), newStatus);
      setApplicant((prev) => prev ? { ...prev, status: newStatus } : null);
    } catch (error) {
      console.error('Status update failed:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!applicant) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Pemohon tidak dijumpai</p>
        <button onClick={() => navigate('/applicants')} className="text-primary hover:underline mt-2">
          Kembali ke senarai
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button onClick={() => navigate('/applicants')} className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
        <ArrowLeft className="w-4 h-4" />
        Kembali
      </button>

      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{applicant.name}</h1>
          <p className="text-gray-500">IC: {applicant.ic_number}</p>
        </div>
        <span className={`px-3 py-1 text-sm font-medium rounded-full ${
          applicant.status === 'approved' ? 'bg-green-100 text-green-700' :
          applicant.status === 'rejected' ? 'bg-red-100 text-red-700' :
          applicant.status === 'reviewing' ? 'bg-yellow-100 text-yellow-700' :
          'bg-gray-100 text-gray-700'
        }`}>
          {applicant.status.toUpperCase()}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main info */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <h2 className="text-lg font-semibold mb-4">Maklumat Peribadi</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="font-medium">{applicant.email || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">No. Telefon</p>
                <p className="font-medium">{applicant.phone || '-'}</p>
              </div>
              <div className="col-span-2">
                <p className="text-sm text-gray-500">Alamat</p>
                <p className="font-medium">{applicant.address || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Bandar</p>
                <p className="font-medium">{applicant.city || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Negeri</p>
                <p className="font-medium">{applicant.state || '-'}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <h2 className="text-lg font-semibold mb-4">Maklumat Kewangan</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Pendapatan Bulanan</p>
                <p className="text-2xl font-bold text-primary">RM{applicant.monthly_income.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Saiz Isi Rumah</p>
                <p className="text-2xl font-bold">{applicant.household_size} orang</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Pekerjaan</p>
                <p className="font-medium">{applicant.occupation || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Majikan</p>
                <p className="font-medium">{applicant.employer || '-'}</p>
              </div>
            </div>
          </div>

          {/* Documents */}
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <h2 className="text-lg font-semibold mb-4">Dokumen</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-gray-400" />
                  <span className="text-sm">Salinan IC</span>
                </div>
                <button className="text-primary text-sm hover:underline">Muat Naik</button>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-gray-400" />
                  <span className="text-sm">Slip Gaji</span>
                </div>
                <button className="text-primary text-sm hover:underline">Muat Naik</button>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-gray-400" />
                  <span className="text-sm">Bil Utiliti</span>
                </div>
                <button className="text-primary text-sm hover:underline">Muat Naik</button>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar - AI Assessment */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <h2 className="text-lg font-semibold mb-4">Penilaian AI</h2>

            {!applicant.eligibility_score ? (
              <button
                onClick={handleAssess}
                disabled={assessing}
                className="w-full py-3 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50"
              >
                {assessing ? 'Menilai...' : 'Jalankan Penilaian AI'}
              </button>
            ) : (
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-500">Skor Kelayakan</span>
                    <span className="font-bold text-green-600">{(applicant.eligibility_score * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full">
                    <div
                      className="h-2 bg-green-500 rounded-full"
                      style={{ width: `${applicant.eligibility_score * 100}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-500">Risiko Penipuan</span>
                    <span className={`font-bold ${applicant.fraud_risk_score && applicant.fraud_risk_score > 0.5 ? 'text-red-600' : 'text-green-600'}`}>
                      {(applicant.fraud_risk_score ? applicant.fraud_risk_score * 100 : 0).toFixed(0)}%
                    </span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full">
                    <div
                      className={`h-2 rounded-full ${applicant.fraud_risk_score && applicant.fraud_risk_score > 0.5 ? 'bg-red-500' : 'bg-green-500'}`}
                      style={{ width: `${(applicant.fraud_risk_score || 0) * 100}%` }}
                    />
                  </div>
                </div>

                {applicant.is_fraud_detected && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center gap-2 text-red-700">
                      <AlertTriangle className="w-4 h-4" />
                      <span className="text-sm font-medium">Risiko Penipuan Dikesan</span>
                    </div>
                    <p className="text-sm text-red-600 mt-1">{applicant.fraud_reasons}</p>
                  </div>
                )}

                <div className="pt-4 border-t">
                  <p className="text-sm text-gray-500 mb-2">Kategori Asnaf</p>
                  <p className="font-medium text-lg capitalize">{applicant.asnaf_category || 'Belum ditentukan'}</p>
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <h2 className="text-lg font-semibold mb-4">Tindakan</h2>
            <div className="space-y-2">
              <button
                onClick={() => handleStatusChange('approved')}
                disabled={applicant.status === 'approved'}
                className="w-full flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 disabled:opacity-50"
              >
                <CheckCircle className="w-4 h-4" />
                Luluskan
              </button>
              <button
                onClick={() => handleStatusChange('rejected')}
                disabled={applicant.status === 'rejected'}
                className="w-full flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 disabled:opacity-50"
              >
                <XCircle className="w-4 h-4" />
                Tolak
              </button>
              <button
                onClick={() => handleStatusChange('reviewing')}
                disabled={applicant.status === 'reviewing'}
                className="w-full flex items-center gap-2 px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 disabled:opacity-50"
              >
                <AlertTriangle className="w-4 h-4" />
                Dalam Semakan
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}