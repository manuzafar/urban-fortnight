/**
 * Context Library Component
 *
 * Allows users to upload, manage, and select enterprise context files
 * that provide organizational guidelines for AI agents.
 */

import { useState, useEffect, useRef } from 'react';
import {
  Building2,
  Layers,
  Users,
  Upload,
  X,
  Check,
  AlertCircle,
  FileText,
  Trash2,
  Eye,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import type {
  EnterpriseContextListItem,
  ContextSelectionState,
  ContextType,
  MergedContextPreview,
} from '../../types/enterpriseContext';
import {
  listEnterpriseContexts,
  uploadContextFile,
  deleteEnterpriseContext,
  previewMergedContext,
} from '../../api/client';

interface ContextLibraryProps {
  isOpen: boolean;
  onClose: () => void;
  selectedContexts: ContextSelectionState;
  onSelectionChange: (selection: ContextSelectionState) => void;
}

const CONTEXT_TYPE_CONFIG: Record<ContextType, {
  icon: typeof Building2;
  label: string;
  description: string;
  color: string;
}> = {
  company: {
    icon: Building2,
    label: 'Company',
    description: 'Organization-wide context',
    color: 'var(--v4-accent)',
  },
  division: {
    icon: Layers,
    label: 'Division',
    description: 'Division-level context',
    color: 'var(--v4-info)',
  },
  team: {
    icon: Users,
    label: 'Team',
    description: 'Team-specific context',
    color: 'var(--v4-success)',
  },
};

export function ContextLibrary({
  isOpen,
  onClose,
  selectedContexts,
  onSelectionChange,
}: ContextLibraryProps) {
  const [contexts, setContexts] = useState<EnterpriseContextListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [expandedType, setExpandedType] = useState<ContextType | null>('company');
  const [preview, setPreview] = useState<MergedContextPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch contexts on open
  useEffect(() => {
    if (isOpen) {
      fetchContexts();
    }
  }, [isOpen]);

  // Update preview when selection changes
  useEffect(() => {
    const selectedId = selectedContexts.company?.id ||
                       selectedContexts.division?.id ||
                       selectedContexts.team?.id;
    if (selectedId) {
      loadPreview(selectedId);
    } else {
      setPreview(null);
    }
  }, [selectedContexts]);

  const fetchContexts = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listEnterpriseContexts();
      setContexts(response.contexts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load contexts');
    } finally {
      setLoading(false);
    }
  };

  const loadPreview = async (contextId: string) => {
    setPreviewLoading(true);
    try {
      const data = await previewMergedContext(contextId);
      setPreview(data);
    } catch (err) {
      console.error('Failed to load preview:', err);
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      await uploadContextFile(file);
      await fetchContexts();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDelete = async (contextId: string) => {
    if (!confirm('Delete this context?')) return;

    try {
      await deleteEnterpriseContext(contextId);
      // Remove from selection if selected
      const newSelection = { ...selectedContexts };
      if (newSelection.company?.id === contextId) delete newSelection.company;
      if (newSelection.division?.id === contextId) delete newSelection.division;
      if (newSelection.team?.id === contextId) delete newSelection.team;
      onSelectionChange(newSelection);
      await fetchContexts();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete context');
    }
  };

  const handleSelect = (context: EnterpriseContextListItem) => {
    const type = context.context_type;
    const isSelected = selectedContexts[type]?.id === context.id;

    const newSelection = { ...selectedContexts };
    if (isSelected) {
      delete newSelection[type];
    } else {
      newSelection[type] = context;
    }

    onSelectionChange(newSelection);
  };

  const getContextsByType = (type: ContextType) =>
    contexts.filter((c) => c.context_type === type);

  const getSelectedCount = () =>
    [selectedContexts.company, selectedContexts.division, selectedContexts.team].filter(Boolean).length;

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        style={{
          background: 'var(--v4-surface)',
          borderRadius: '16px',
          width: '90%',
          maxWidth: '900px',
          maxHeight: '85vh',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: '20px 24px',
            borderBottom: '1px solid var(--v4-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '4px' }}>
              Enterprise Context
            </h2>
            <p style={{ fontSize: '13px', color: 'var(--v4-text-muted)' }}>
              Attach organizational guidelines for AI agents
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '8px',
              color: 'var(--v4-text-muted)',
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
          {/* Left Panel: Context List */}
          <div
            style={{
              flex: '0 0 55%',
              borderRight: '1px solid var(--v4-border)',
              overflow: 'auto',
              padding: '16px',
            }}
          >
            {/* Upload Button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              style={{
                width: '100%',
                padding: '16px',
                border: '2px dashed var(--v4-border)',
                borderRadius: '12px',
                background: 'var(--v4-background)',
                cursor: uploading ? 'wait' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '12px',
                marginBottom: '20px',
              }}
            >
              <Upload size={20} style={{ color: 'var(--v4-text-muted)' }} />
              <span style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>
                {uploading ? 'Uploading...' : 'Upload context file (.md, .yaml)'}
              </span>
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".md,.yaml,.yml"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />

            {error && (
              <div
                style={{
                  padding: '12px 16px',
                  background: 'var(--v4-error-light)',
                  borderRadius: '8px',
                  marginBottom: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <AlertCircle size={16} style={{ color: 'var(--v4-error)' }} />
                <span style={{ fontSize: '13px', color: 'var(--v4-error)' }}>{error}</span>
              </div>
            )}

            {loading ? (
              <div style={{ textAlign: 'center', padding: '40px', color: 'var(--v4-text-muted)' }}>
                Loading contexts...
              </div>
            ) : contexts.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <FileText size={40} style={{ color: 'var(--v4-text-muted)', marginBottom: '12px' }} />
                <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', marginBottom: '4px' }}>
                  No contexts yet
                </p>
                <p style={{ fontSize: '13px', color: 'var(--v4-text-muted)' }}>
                  Upload a markdown or YAML file to get started
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {(['company', 'division', 'team'] as const).map((type) => {
                  const config = CONTEXT_TYPE_CONFIG[type];
                  const Icon = config.icon;
                  const typeContexts = getContextsByType(type);
                  const isExpanded = expandedType === type;
                  const selectedInType = selectedContexts[type];

                  return (
                    <div key={type}>
                      <button
                        onClick={() => setExpandedType(isExpanded ? null : type)}
                        style={{
                          width: '100%',
                          padding: '12px 16px',
                          border: '1px solid var(--v4-border)',
                          borderRadius: '10px',
                          background: 'var(--v4-surface)',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px',
                        }}
                      >
                        <Icon size={18} style={{ color: config.color }} />
                        <span style={{ flex: 1, textAlign: 'left', fontWeight: 500 }}>
                          {config.label}
                          <span style={{ fontWeight: 400, color: 'var(--v4-text-muted)', marginLeft: '8px' }}>
                            ({typeContexts.length})
                          </span>
                        </span>
                        {selectedInType && (
                          <span
                            style={{
                              padding: '2px 8px',
                              background: 'var(--v4-accent-light)',
                              color: 'var(--v4-accent)',
                              fontSize: '11px',
                              fontWeight: 600,
                              borderRadius: '10px',
                            }}
                          >
                            Selected
                          </span>
                        )}
                        {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                      </button>

                      {isExpanded && (
                        <div style={{ paddingLeft: '24px', paddingTop: '8px' }}>
                          {typeContexts.length === 0 ? (
                            <p style={{ fontSize: '13px', color: 'var(--v4-text-muted)', padding: '12px 0' }}>
                              No {config.label.toLowerCase()} contexts
                            </p>
                          ) : (
                            typeContexts.map((context) => {
                              const isSelected = selectedContexts[type]?.id === context.id;
                              return (
                                <div
                                  key={context.id}
                                  style={{
                                    padding: '12px',
                                    border: isSelected ? `2px solid ${config.color}` : '1px solid var(--v4-border)',
                                    borderRadius: '8px',
                                    marginBottom: '8px',
                                    background: isSelected ? 'var(--v4-accent-light)' : 'var(--v4-background)',
                                    cursor: 'pointer',
                                  }}
                                  onClick={() => handleSelect(context)}
                                >
                                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                      {isSelected ? (
                                        <Check size={16} style={{ color: config.color }} />
                                      ) : (
                                        <div
                                          style={{
                                            width: '16px',
                                            height: '16px',
                                            border: '2px solid var(--v4-border)',
                                            borderRadius: '4px',
                                          }}
                                        />
                                      )}
                                      <span style={{ fontWeight: 500, fontSize: '14px' }}>{context.name}</span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                      <StatusBadge status={context.validation_status} />
                                      <button
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleDelete(context.id);
                                        }}
                                        style={{
                                          background: 'none',
                                          border: 'none',
                                          cursor: 'pointer',
                                          padding: '4px',
                                          color: 'var(--v4-text-muted)',
                                        }}
                                      >
                                        <Trash2 size={14} />
                                      </button>
                                    </div>
                                  </div>
                                </div>
                              );
                            })
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Right Panel: Preview */}
          <div style={{ flex: '0 0 45%', overflow: 'auto', padding: '16px' }}>
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '4px' }}>
                Merged Context Preview
              </h3>
              <p style={{ fontSize: '12px', color: 'var(--v4-text-muted)' }}>
                Shows the effective context from selected files
              </p>
            </div>

            {previewLoading ? (
              <div style={{ textAlign: 'center', padding: '40px', color: 'var(--v4-text-muted)' }}>
                Loading preview...
              </div>
            ) : preview ? (
              <div style={{ fontSize: '13px' }}>
                {preview.sources.length > 0 && (
                  <div style={{ marginBottom: '16px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--v4-text-muted)', textTransform: 'uppercase' }}>
                      Sources
                    </span>
                    <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                      {preview.sources.map((s) => (
                        <span
                          key={s}
                          style={{
                            padding: '4px 10px',
                            background: 'var(--v4-accent-light)',
                            color: 'var(--v4-accent)',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: 500,
                          }}
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {preview.constraints_preview.length > 0 && (
                  <div>
                    <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--v4-text-muted)', textTransform: 'uppercase' }}>
                      Constraints ({preview.constraints_preview.length})
                    </span>
                    <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {preview.constraints_preview.slice(0, 5).map((c, i) => (
                        <div
                          key={i}
                          style={{
                            padding: '10px 12px',
                            background: 'var(--v4-background)',
                            borderRadius: '8px',
                            border: '1px solid var(--v4-border)',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                            <span
                              style={{
                                padding: '2px 6px',
                                background: c.constraint_type === 'must_use' ? 'var(--v4-error-light)' : 'var(--v4-info-light)',
                                color: c.constraint_type === 'must_use' ? 'var(--v4-error)' : 'var(--v4-info)',
                                fontSize: '10px',
                                fontWeight: 600,
                                borderRadius: '4px',
                              }}
                            >
                              {c.constraint_type}
                            </span>
                            <span style={{ fontSize: '12px', color: 'var(--v4-text-muted)' }}>
                              {c.field}
                            </span>
                          </div>
                          <div style={{ fontSize: '13px', color: 'var(--v4-text)' }}>
                            {String(c.value)}
                          </div>
                        </div>
                      ))}
                      {preview.constraints_preview.length > 5 && (
                        <p style={{ fontSize: '12px', color: 'var(--v4-text-muted)' }}>
                          +{preview.constraints_preview.length - 5} more constraints
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <Eye size={32} style={{ color: 'var(--v4-text-muted)', marginBottom: '12px' }} />
                <p style={{ fontSize: '13px', color: 'var(--v4-text-muted)' }}>
                  Select a context to preview
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div
          style={{
            padding: '16px 24px',
            borderTop: '1px solid var(--v4-border)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span style={{ fontSize: '13px', color: 'var(--v4-text-muted)' }}>
            {getSelectedCount()} context{getSelectedCount() !== 1 ? 's' : ''} selected
          </span>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={onClose}
              className="v4-btn v4-btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={onClose}
              className="v4-btn v4-btn-primary"
            >
              Apply
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const config = {
    valid: { bg: 'var(--v4-success-light)', color: 'var(--v4-success)', label: 'Valid' },
    invalid: { bg: 'var(--v4-error-light)', color: 'var(--v4-error)', label: 'Invalid' },
    pending: { bg: 'var(--v4-warning-light)', color: 'var(--v4-warning)', label: 'Pending' },
  }[status] || { bg: 'var(--v4-background)', color: 'var(--v4-text-muted)', label: status };

  return (
    <span
      style={{
        padding: '2px 8px',
        background: config.bg,
        color: config.color,
        fontSize: '10px',
        fontWeight: 600,
        borderRadius: '8px',
      }}
    >
      {config.label}
    </span>
  );
}

export default ContextLibrary;
