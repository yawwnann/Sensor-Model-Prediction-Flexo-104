import React from "react";

const Hotspot = ({
  x,
  y,
  label,
  status = "good",
  isActive,
  onMouseEnter,
  onMouseLeave,
  responsive = {}, // { mobile: { x, y }, tablet: { x, y } }
}) => {
  // Map status to color
  const statusColors = {
    good: "bg-green-500",
    warning: "bg-yellow-500",
    critical: "bg-red-500",
    error: "bg-gray-400",
  };

  const bgColor = statusColors[status] || statusColors.good;

  // Get responsive positions
  const mobileX = responsive.mobile?.x || x;
  const mobileY = responsive.mobile?.y || y;
  const tabletX = responsive.tablet?.x || x;
  const tabletY = responsive.tablet?.y || y;

  return (
    <div
      className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer group hotspot-responsive"
      style={{
        // CSS custom properties for responsive positioning
        "--mobile-x": `${mobileX}%`,
        "--mobile-y": `${mobileY}%`,
        "--tablet-x": `${tabletX}%`,
        "--tablet-y": `${tabletY}%`,
        "--desktop-x": `${x}%`,
        "--desktop-y": `${y}%`,
        // Default (mobile)
        top: `var(--mobile-y)`,
        left: `var(--mobile-x)`,
        zIndex: isActive ? 50 : 10,
      }}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {/* Hotspot indicator - responsive sizing */}
      <div
        className={`relative flex items-center justify-center w-5 h-5 md:w-6 md:h-6 rounded-full ${bgColor} transition-transform ${
          isActive ? "scale-125" : "scale-100"
        }`}
      >
        {/* Pulse animation */}
        <div
          className={`animate-pulse absolute inline-flex h-full w-full rounded-full ${bgColor} opacity-75`}
        ></div>
        {/* Inner dot */}
        <div className="relative w-2.5 h-2.5 md:w-3 md:h-3 bg-white rounded-full"></div>
      </div>

      {/* Label tooltip - only show on hover */}
      {isActive && (
        <div className="absolute top-6 md:top-8 left-1/2 -translate-x-1/2 whitespace-nowrap bg-slate-800 text-white text-xs px-2 py-1 rounded shadow-lg pointer-events-none">
          {label}
        </div>
      )}
    </div>
  );
};

export default Hotspot;
