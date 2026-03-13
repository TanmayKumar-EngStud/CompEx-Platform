"use client";

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, X, Download } from 'lucide-react';
import { Button } from '@/shared/components/ui/button';

interface UpdateNotificationProps {
  /** Whether the notification is visible */
  visible: boolean;
  /** Callback when user clicks refresh */
  onRefresh: () => void;
  /** Callback when user dismisses notification */
  onDismiss: () => void;
  /** Build information for the update */
  buildInfo?: {
    version: string;
    buildTime: string;
  } | null;
}

/**
 * Update notification component
 * Shows when a new version is available and prompts user to refresh
 */
export function UpdateNotification({
  visible,
  onRefresh,
  onDismiss,
  buildInfo
}: UpdateNotificationProps) {
  if (!visible) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -100 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -100 }}
        transition={{
          type: "spring",
          stiffness: 300,
          damping: 30
        }}
        className="fixed top-4 left-1/2 transform -translate-x-1/2 z-[9999] max-w-md w-full mx-4"
      >
        <div className="bg-background border border-border rounded-lg shadow-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "linear"
                }}
                className="w-6 h-6 text-primary"
              >
                <Download />
              </motion.div>
            </div>
            
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-medium text-foreground">
                New Version Available
              </h3>
              <p className="text-sm text-muted-foreground mt-1">
                A newer version of CompEx is ready with the latest features and improvements.
              </p>
              
              {buildInfo && (
                <div className="text-xs text-muted-foreground mt-2 space-y-1">
                  <div>Version: {buildInfo.version}</div>
                  <div>Built: {new Date(buildInfo.buildTime).toLocaleString()}</div>
                </div>
              )}
              
              <div className="flex space-x-2 mt-3">
                <Button
                  size="sm"
                  onClick={onRefresh}
                  className="flex items-center space-x-1"
                >
                  <RefreshCw size={14} />
                  <span>Refresh Now</span>
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onDismiss}
                  className="flex items-center space-x-1"
                >
                  <span>Later</span>
                </Button>
              </div>
            </div>
            
            <button
              onClick={onDismiss}
              className="flex-shrink-0 p-1 rounded-md hover:bg-muted transition-colors"
            >
              <X size={16} className="text-muted-foreground" />
            </button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

/**
 * Compact update notification for bottom of screen
 */
export function CompactUpdateNotification({
  visible,
  onRefresh,
  onDismiss
}: Omit<UpdateNotificationProps, 'buildInfo'>) {
  if (!visible) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 100 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 100 }}
        transition={{
          type: "spring",
          stiffness: 300,
          damping: 30
        }}
        className="fixed bottom-4 right-4 z-[9999]"
      >
        <div className="bg-primary text-primary-foreground rounded-lg shadow-lg p-3 flex items-center space-x-3">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "linear"
            }}
          >
            <RefreshCw size={16} />
          </motion.div>
          
          <span className="text-sm font-medium">Update available</span>
          
          <Button
            variant="secondary"
            size="sm"
            onClick={onRefresh}
            className="h-7 px-2 text-xs"
          >
            Refresh
          </Button>
          
          <button
            onClick={onDismiss}
            className="p-1 rounded-md hover:bg-primary-foreground/20 transition-colors"
          >
            <X size={14} />
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}