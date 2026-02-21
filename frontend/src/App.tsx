import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import Applicants from '@/pages/Applicants';
import ApplicantDetail from '@/pages/ApplicantDetail';
import Payments from '@/pages/Payments';
import Chatbot from '@/pages/Chatbot';
import Audit from '@/pages/Audit';
import { User } from '@/types';
import { authApi } from '@/services/api';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      authApi.getMe()
        .then((userData) => setUser(userData))
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={!user ? <Login setUser={setUser} /> : <Navigate to="/" />} />
        <Route element={<Layout user={user} setUser={setUser} />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/applicants" element={<Applicants />} />
          <Route path="/applicants/:id" element={<ApplicantDetail />} />
          <Route path="/payments" element={<Payments />} />
          <Route path="/chatbot" element={<Chatbot />} />
          <Route path="/audit" element={<Audit />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;