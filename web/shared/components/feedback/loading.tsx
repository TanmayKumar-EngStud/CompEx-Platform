import React from "react";

interface LoadingProps {
  size?: "sm" | "md" | "lg";
  message?: string;
  className?: string;
}

const Loading: React.FC<LoadingProps> = ({ 
  size = "md", 
  message = "Loading...", 
  className = "" 
}) => {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-8 h-8", 
    lg: "w-12 h-12"
  };

  return (
    <div className={`flex flex-col items-center justify-center gap-3 ${className}`}>
      <div
        className={`${sizeClasses[size]} border-2 border-muted-foreground/30 border-t-primary rounded-full animate-spin`}
      />
      {message && (
        <span className="text-muted-foreground text-sm animate-pulse">
          {message}
        </span>
      )}
    </div>
  );
};

export default Loading;