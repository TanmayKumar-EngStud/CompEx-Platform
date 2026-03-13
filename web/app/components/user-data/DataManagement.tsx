// User Data Management Component
// Transparent data ownership - users control their data

'use client';

import { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from 'react-native';

interface DataManagementProps {
  userId: number;
}

export default function DataManagement({ userId }: DataManagementProps) {
  const [exporting, setExporting] = useState(false);
  const [importing, setImporting] = useState(false);
  const [lastExport, setLastExport] = useState<string | null>(null);

  const handleExport = async () => {
    try {
      setExporting(true);
      
      const response = await fetch('/api/user/export-data', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Export failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `compex-data-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setLastExport(new Date().toLocaleString());
      Alert.alert('Success', 'Your data has been downloaded!');
      
    } catch (error) {
      Alert.alert('Error', 'Failed to export data. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  const handleImport = async () => {
    // Create file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e: any) => {
      const file = e.target.files[0];
      if (!file) return;

      try {
        setImporting(true);
        const text = await file.text();
        const data = JSON.parse(text);

        const response = await fetch('/api/user/import-data', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });

        const result = await response.json();

        if (result.success) {
          Alert.alert('Success', result.message);
        } else {
          Alert.alert('Import Failed', result.error);
        }
      } catch (error) {
        Alert.alert('Error', 'Failed to read file. Please try again.');
      } finally {
        setImporting(false);
      }
    };
    input.click();
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>📦 Your Data</Text>
      
      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>🔒 Your Data is Yours</Text>
        <Text style={styles.infoText}>
          You can download all your data at any time, or import a backup to restore your progress.
        </Text>
      </View>

      <View style={styles.dataTypes}>
        <Text style={styles.sectionTitle}>What you own:</Text>
        <View style={styles.dataList}>
          <DataItem text="✓ Questions answered" />
          <DataItem text="✓ Accuracy scores" />
          <DataItem text="✓ Topic progress" />
          <DataItem text="✓ Learning streaks" />
          <DataItem text="✓ Achievements & badges" />
          <DataItem text="✓ Preferences & settings" />
        </View>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.button, styles.exportButton]}
          onPress={handleExport}
          disabled={exporting}
        >
          {exporting ? (
            <ActivityIndicator color="white" />
          ) : (
            <>
              <Text style={styles.buttonText}>📥 Download My Data</Text>
            </>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.importButton]}
          onPress={handleImport}
          disabled={importing}
        >
          {importing ? (
            <ActivityIndicator color="white" />
          ) : (
            <>
              <Text style={styles.buttonText}>📤 Import Backup</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      {lastExport && (
        <Text style={styles.lastExport}>
          Last exported: {lastExport}
        </Text>
      )}

      <View style={styles.securityNote}>
        <Text style={styles.securityTitle}>🔐 Security</Text>
        <Text style={styles.securityText}>
          Your data is encrypted and never shared with third parties. 
          We comply with GDPR and data protection regulations.
        </Text>
      </View>

      <View style={styles.deleteAccount}>
        <TouchableOpacity
          style={[styles.button, styles.deleteButton]}
          onPress={() => Alert.alert(
            'Delete Account',
            'This will permanently delete your account and all data. This action cannot be undone.',
            [
              { text: 'Cancel', style: 'cancel' },
              { 
                text: 'Delete', 
                style: 'destructive',
                onPress: () => Alert.alert('Contact Support', 'Please contact support@compex.live to delete your account.')
              }
            ]
          )}
        >
          <Text style={[styles.buttonText, styles.deleteButtonText]}>
            Delete My Account
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

function DataItem({ text }: { text: string }) {
  return (
    <View style={styles.dataItem}>
      <Text style={styles.dataItemText}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#1a1a1a',
  },
  infoCard: {
    backgroundColor: '#f0f7ff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#0066ff',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#1a1a1a',
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  dataTypes: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
    color: '#1a1a1a',
  },
  dataList: {
    gap: 8,
  },
  dataItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dataItemText: {
    fontSize: 14,
    color: '#444',
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  button: {
    flex: 1,
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 10,
    alignItems: 'center',
  },
  exportButton: {
    backgroundColor: '#0066ff',
  },
  importButton: {
    backgroundColor: '#00a855',
  },
  buttonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  lastExport: {
    fontSize: 12,
    color: '#888',
    textAlign: 'center',
    marginBottom: 20,
  },
  securityNote: {
    backgroundColor: '#f8f9fb',
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
  },
  securityTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    color: '#1a1a1a',
  },
  securityText: {
    fontSize: 12,
    color: '#666',
    lineHeight: 18,
  },
  deleteAccount: {
    marginTop: 20,
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  deleteButton: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#dc3545',
  },
  deleteButtonText: {
    color: '#dc3545',
  },
});
