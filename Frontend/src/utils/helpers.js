import { CheckCircle, AlertTriangle, Settings } from 'lucide-react';

export const getStatusInfo = (health) => {
  switch (health) {
    case 'good':
      return { 
        text: 'Baik', 
        color: 'text-green-500', 
        bgColor: 'bg-green-500', 
        Icon: CheckCircle 
      };
    case 'warning':
      return { 
        text: 'Perhatian', 
        color: 'text-yellow-500', 
        bgColor: 'bg-yellow-500', 
        Icon: AlertTriangle 
      };
    case 'critical':
      return { 
        text: 'Kritis', 
        color: 'text-red-500', 
        bgColor: 'bg-red-500', 
        Icon: AlertTriangle 
      };
    default:
      return { 
        text: 'Unknown', 
        color: 'text-gray-500', 
        bgColor: 'bg-gray-500', 
        Icon: Settings 
      };
  }
};

export const getStatusInfoCard = (health) => {
  switch (health) {
    case 'good': 
      return { 
        text: 'Baik', 
        color: 'text-green-700', 
        bgColor: 'bg-green-50', 
        strongBgColor: 'bg-green-500', 
        ringColor: 'ring-green-500', 
        Icon: CheckCircle 
      };
    case 'warning': 
      return { 
        text: 'Perhatian', 
        color: 'text-yellow-700', 
        bgColor: 'bg-yellow-50', 
        strongBgColor: 'bg-yellow-500', 
        ringColor: 'ring-yellow-500', 
        Icon: AlertTriangle 
      };
    case 'critical': 
      return { 
        text: 'Kritis', 
        color: 'text-red-700', 
        bgColor: 'bg-red-50', 
        strongBgColor: 'bg-red-500', 
        ringColor: 'ring-red-500', 
        Icon: AlertTriangle 
      };
    default: 
      return { 
        text: 'Unknown', 
        color: 'text-gray-700', 
        bgColor: 'bg-gray-50', 
        strongBgColor: 'bg-gray-500', 
        ringColor: 'ring-gray-500', 
        Icon: Settings 
      };
  }
};

export const getOverallStatus = (components) => {
    if (!components || components.length === 0) return getStatusInfo('unknown');
    if (components.some(c => c.health === 'critical')) return getStatusInfo('critical');
    if (components.some(c => c.health === 'warning')) return getStatusInfo('warning');
    return getStatusInfo('good');
};
