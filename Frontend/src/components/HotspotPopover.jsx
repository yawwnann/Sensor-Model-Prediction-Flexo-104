import React from 'react';
import { CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

const HotspotPopover = ({ x, y, data }) => {
    if (!data) return null;

    // Determine status based on health score
    const getStatus = (health) => {
        if (health >= 80) return { text: 'Baik', color: 'text-green-600', icon: CheckCircle, bgColor: 'bg-green-500' };
        if (health >= 60) return { text: 'Perhatian', color: 'text-yellow-600', icon: AlertTriangle, bgColor: 'bg-yellow-500' };
        return { text: 'Kritis', color: 'text-red-600', icon: XCircle, bgColor: 'bg-red-500' };
    };

    const status = getStatus(data.health || 0);
    const StatusIcon = status.icon;

    return (
        <div
            className="absolute z-[9999] pointer-events-none"
            style={{
                top: `${y}%`,
                left: `${x}%`,
                transform: 'translate(-50%, calc(-100% - 20px))',
                minWidth: '250px',
            }}
        >
            <div className="relative p-4 bg-white border border-slate-200 rounded-lg shadow-xl">
                {/* Header */}
                <div className={`flex items-center font-bold mb-3 ${status.color}`}>
                    <StatusIcon className="w-5 h-5 mr-2 flex-shrink-0" />
                    <h4 className="text-lg leading-tight">{data.name}</h4>
                </div>

                {/* Info Grid */}
                <div className="grid grid-cols-[auto,1fr] gap-x-4 gap-y-2 text-sm mb-4">
                    <span className="text-slate-600">Status:</span>
                    <span className={`font-semibold ${status.color}`}>{status.text}</span>
                    
                    <span className="text-slate-600">Skor:</span>
                    <span className="font-semibold text-slate-900">{Math.round(data.health)}/100</span>
                    
                    {data.maintenanceDays !== undefined && data.maintenanceDays !== null && (
                        <>
                            <span className="text-slate-600">Maintenance:</span>
                            <span className="font-semibold text-slate-900">{data.maintenanceDays} hari</span>
                        </>
                    )}
                </div>

                {/* Health Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                    <div 
                        className={`${status.bgColor} h-2 rounded-full transition-all`} 
                        style={{ width: `${Math.min(100, Math.max(0, data.health))}%` }}
                    ></div>
                </div>

                {/* Footer */}
                <div className="pt-2 text-xs text-center text-slate-400 border-t border-slate-200">
                    Hover untuk detail
                </div>

                {/* Arrow pointer */}
                <div className="absolute w-4 h-4 bg-white border-r border-b border-slate-200 rotate-45 -bottom-2 left-1/2 -translate-x-1/2"></div>
            </div>
        </div>
    );
};

export default HotspotPopover;
