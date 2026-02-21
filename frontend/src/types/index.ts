export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: number;
  created_at: string;
  updated_at: string;
}

export interface Applicant {
  id: number;
  ic_number: string;
  name: string;
  email?: string;
  phone?: string;
  address?: string;
  postcode?: string;
  city?: string;
  state?: string;
  monthly_income: number;
  household_size: number;
  occupation?: string;
  employer?: string;
  eligibility_score?: number;
  fraud_risk_score?: number;
  is_fraud_detected?: boolean;
  fraud_reasons?: string;
  status: string;
  asnaf_category?: string;
  latitude?: number;
  longitude?: number;
  created_at: string;
  updated_at?: string;
  documents?: Document[];
}

export interface Document {
  id: number;
  applicant_id: number;
  document_type: string;
  file_path: string;
  file_name: string;
  file_size?: number;
  mime_type?: string;
  extracted_text?: string;
  is_verified: boolean;
  verification_notes?: string;
  created_at: string;
}

export interface Payment {
  id: number;
  applicant_id: number;
  payment_reference: string;
  amount: number;
  payment_method?: string;
  status: string;
  bank_name?: string;
  account_number?: string;
  account_holder_name?: string;
  transaction_date?: string;
  transaction_id?: string;
  approved_by?: number;
  approved_at?: string;
  notes?: string;
  is_anomaly?: boolean;
  anomaly_reason?: string;
  created_at: string;
  updated_at?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface DashboardStats {
  total_applicants: number;
  by_status: Record<string, number>;
  recent_applications: number;
  pending_payments: number;
  avg_processing_days: number;
  fraud_alerts: number;
}

export interface CriticalCase {
  type: string;
  severity: 'tinggi' | 'sederhana' | 'rendah';
  applicant_id: number;
  applicant_name: string;
  ic_number: string;
  days_pending?: number;
  description: string;
  recommended_action: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}