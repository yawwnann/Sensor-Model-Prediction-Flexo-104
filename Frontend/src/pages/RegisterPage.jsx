import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const RegisterPage = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        
        // Mock registration - untuk demo saja
        // Validasi sederhana
        if (!name || name.trim().length < 3) {
            setError('Nama minimal 3 karakter');
            setLoading(false);
            return;
        }
        
        if (!email || !email.includes('@')) {
            setError('Email tidak valid');
            setLoading(false);
            return;
        }
        
        if (!password || password.length < 6) {
            setError('Password minimal 6 karakter');
            setLoading(false);
            return;
        }

        try {
            // Simulasi delay registrasi
            await new Promise(resolve => setTimeout(resolve, 800));
            
            // Simpan user ke localStorage untuk demo
            const users = JSON.parse(localStorage.getItem('users') || '[]');
            users.push({ name, email, password });
            localStorage.setItem('users', JSON.stringify(users));
            
            navigate('/login'); // Arahkan ke halaman login setelah registrasi berhasil
        } catch (err) {
            setError('Registrasi gagal. Coba lagi nanti.');
            console.error(err);
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
                        <h2 className="text-3xl font-bold text-gray-800">Buat Akun Baru</h2>
                        <p className="mt-2 text-gray-600">Digital Twin Flexo Machine Monitoring</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label htmlFor="name" className="text-sm font-medium text-gray-700">Nama Lengkap</label>
                        <input id="name" type="text" value={name} onChange={(e) => setName(e.target.value)} required className="w-full px-4 py-2 mt-2 border border-gray-300 rounded-lg focus:ring-sky-500 focus:border-sky-500" />
                    </div>
                    <div>
                        <label htmlFor="email" className="text-sm font-medium text-gray-700">Email</label>
                        <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full px-4 py-2 mt-2 border border-gray-300 rounded-lg focus:ring-sky-500 focus:border-sky-500" />
                    </div>
                    <div>
                        <label htmlFor="password" className="text-sm font-medium text-gray-700">Password</label>
                        <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full px-4 py-2 mt-2 border border-gray-300 rounded-lg focus:ring-sky-500 focus:border-sky-500" />
                    </div>
                    {error && <p className="text-sm text-red-600">{error}</p>}
                    <div>
                        <button type="submit" disabled={loading} className="w-full px-4 py-2 font-semibold text-white bg-sky-500 rounded-lg hover:bg-sky-600 disabled:bg-sky-300">
                            {loading ? 'Mendaftarkan...' : 'Daftar'}
                        </button>
                    </div>
                </form>
                
                <p className="text-sm text-center text-gray-600">
                    Sudah punya akun? {' '}
                    <Link to="/login" className="font-medium text-sky-500 hover:underline">
                        Login
                    </Link>
                </p>
            </div>
        </div>
    );
};

export default RegisterPage;
