import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const LoginPage = ({ onLogin }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        
        if (!email || !password) {
            setError('Email dan password harus diisi');
            setLoading(false);
            return;
        }
        
        try {
            // Simple client-side auth for demo
            // In production, this should call a real backend API
            if (email && password.length >= 6) {
                // Mock successful login
                localStorage.setItem('token', 'demo-token-' + Date.now());
                localStorage.setItem('user', email);
                onLogin();
                navigate('/dashboard');
            } else {
                throw new Error('Password minimal 6 karakter');
            }
        } catch (err) {
            setError('Login gagal. Periksa kembali email dan password Anda.');
            console.error('Login error:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-slate-100">
            <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-xl shadow-lg">
                <div className="text-center space-y-4">
                    <img 
                        src="/dtfm2.png" 
                        alt="Digital Twin Logo" 
                        className="h-16 w-auto mx-auto"
                    />
                    <div>
                        <h2 className="text-3xl font-bold text-gray-800">Selamat Datang</h2>
                        <p className="mt-2 text-gray-600">Digital Twin Flexo Machine Monitoring</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label htmlFor="email" className="text-sm font-medium text-gray-700">Email</label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="w-full px-4 py-2 mt-2 border border-gray-300 rounded-lg focus:ring-sky-500 focus:border-sky-500"
                            placeholder="anda@email.com"
                        />
                    </div>
                    <div>
                        <label htmlFor="password" className="text-sm font-medium text-gray-700">Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="w-full px-4 py-2 mt-2 border border-gray-300 rounded-lg focus:ring-sky-500 focus:border-sky-500"
                            placeholder="••••••••"
                        />
                    </div>
                    {error && <p className="text-sm text-red-600">{error}</p>}
                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full px-4 py-2 font-semibold text-white bg-sky-500 rounded-lg hover:bg-sky-600 disabled:bg-sky-300"
                        >
                            {loading ? 'Memproses...' : 'Login'}
                        </button>
                    </div>
                </form>
                
                <p className="text-sm text-center text-gray-600">
                    Belum punya akun? {' '}
                    <Link to="/register" className="font-medium text-sky-500 hover:underline">
                        Daftar di sini
                    </Link>
                </p>
            </div>
        </div>
    );
};

export default LoginPage;
