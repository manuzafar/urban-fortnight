import { useState, useRef, useEffect } from 'react';
import { Download, ChevronDown, FileText, File, FileJson, Loader2 } from 'lucide-react';
import { exportPdf, exportDocx } from '../api/client';

interface ExportDropdownProps {
  sessionId: string;
  currentSection?: string;
  onExportJson: () => void;
}

type ExportFormat = 'pdf' | 'docx';

export function ExportDropdown({ sessionId, currentSection, onExportJson }: ExportDropdownProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleExport = async (format: ExportFormat, section?: string) => {
    const loadingKey = `${format}-${section || 'full'}`;
    setLoading(loadingKey);

    try {
      let blob: Blob;
      if (format === 'pdf') {
        blob = await exportPdf(sessionId, section);
      } else {
        blob = await exportDocx(sessionId, section);
      }

      // Create download link
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      const filename = section
        ? `${section.replace(/_/g, '-')}-${sessionId.slice(0, 8)}.${format}`
        : `inception-pack-${sessionId.slice(0, 8)}.${format}`;
      a.download = filename;

      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setOpen(false);
    } catch (error) {
      console.error(`Failed to export ${format}:`, error);
      alert(`Failed to export ${format.toUpperCase()}. Please try again.`);
    } finally {
      setLoading(null);
    }
  };

  const renderLoadingOrIcon = (loadingKey: string, Icon: typeof FileText) => {
    if (loading === loadingKey) {
      return <Loader2 size={14} className="export-loading-icon" />;
    }
    return <Icon size={14} />;
  };

  return (
    <div className="export-dropdown" ref={dropdownRef} data-tour="export-button">
      <button
        onClick={() => setOpen(!open)}
        className="export-button"
        disabled={loading !== null}
      >
        {loading ? <Loader2 size={16} className="export-loading-icon" /> : <Download size={16} />}
        Export
        <ChevronDown size={14} className={`export-chevron ${open ? 'open' : ''}`} />
      </button>

      {open && (
        <div className="export-menu">
          <div className="export-menu-section">
            <div className="export-menu-label">Full Pack</div>
            <button
              onClick={() => handleExport('pdf')}
              disabled={loading !== null}
              className="export-menu-item"
            >
              {renderLoadingOrIcon('pdf-full', FileText)}
              PDF Document
            </button>
            <button
              onClick={() => handleExport('docx')}
              disabled={loading !== null}
              className="export-menu-item"
            >
              {renderLoadingOrIcon('docx-full', File)}
              Word Document
            </button>
            <button
              onClick={() => {
                onExportJson();
                setOpen(false);
              }}
              disabled={loading !== null}
              className="export-menu-item"
            >
              <FileJson size={14} />
              JSON Data
            </button>
          </div>

          {currentSection && (
            <>
              <div className="export-menu-divider" />
              <div className="export-menu-section">
                <div className="export-menu-label">Current Section</div>
                <button
                  onClick={() => handleExport('pdf', currentSection)}
                  disabled={loading !== null}
                  className="export-menu-item"
                >
                  {renderLoadingOrIcon(`pdf-${currentSection}`, FileText)}
                  {formatSectionName(currentSection)} (PDF)
                </button>
                <button
                  onClick={() => handleExport('docx', currentSection)}
                  disabled={loading !== null}
                  className="export-menu-item"
                >
                  {renderLoadingOrIcon(`docx-${currentSection}`, File)}
                  {formatSectionName(currentSection)} (Word)
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

function formatSectionName(section: string): string {
  return section
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
