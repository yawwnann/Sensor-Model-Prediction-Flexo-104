import React from 'react';

const Hotspot = ({ x, y, label, status = 'good', isActive, onMouseEnter, onMouseLeave }) => {
    // Map status to color
    const statusColors = {
        good: 'bg-green-500',
        warning: 'bg-yellow-500',
        critical: 'bg-red-500',
        error: 'bg-gray-400',
    };

    const bgColor = statusColors[status] || statusColors.good;

    return (
        <div
            className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer group"
            style={{ 
                top: `${y}%`, 
                left: `${x}%`,
                zIndex: isActive ? 50 : 10,
            }}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave}
        >
            {/* Hotspot indicator */}
            <div className={`relative flex items-center justify-center w-6 h-6 rounded-full ${bgColor} transition-transform ${isActive ? 'scale-125' : 'scale-100'}`}>
                {/* Pulse animation */}
                <div className={`animate-pulse absolute inline-flex h-full w-full rounded-full ${bgColor} opacity-75`}></div>
                {/* Inner dot */}
                <div className="relative w-3 h-3 bg-white rounded-full"></div>
            </div>

            {/* Label tooltip - only show on hover */}
            {isActive && (
                <div className="absolute top-8 left-1/2 -translate-x-1/2 whitespace-nowrap bg-slate-800 text-white text-xs px-2 py-1 rounded shadow-lg pointer-events-none">
                    {label}
                </div>
            )}
        </div>
    );
};

export default Hotspot;
