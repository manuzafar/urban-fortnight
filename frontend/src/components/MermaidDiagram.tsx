import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

interface MermaidDiagramProps {
  chart: string;
}

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#6d5efc',
    primaryTextColor: '#e0e0e0',
    primaryBorderColor: '#8b7cff',
    lineColor: '#555',
    secondaryColor: '#2a2a3e',
    tertiaryColor: '#1e1e2e',
    background: '#141422',
    mainBkg: '#1e1e2e',
    nodeBorder: '#6d5efc',
    clusterBkg: 'rgba(109, 94, 252, 0.08)',
    clusterBorder: 'rgba(109, 94, 252, 0.3)',
    titleColor: '#e0e0e0',
    edgeLabelBackground: '#1e1e2e',
  },
  flowchart: {
    htmlLabels: true,
    curve: 'basis',
    padding: 16,
  },
  securityLevel: 'loose',
});

let diagramCounter = 0;

export function MermaidDiagram({ chart }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [idRef] = useState(() => `mermaid-diagram-${++diagramCounter}`);

  useEffect(() => {
    if (!chart || !containerRef.current) return;

    const renderDiagram = async () => {
      try {
        setError(null);
        containerRef.current!.innerHTML = '';
        const { svg } = await mermaid.render(idRef, chart);
        if (containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      } catch (err) {
        console.error('Mermaid render error:', err);
        setError('Diagram could not be rendered');
      }
    };

    renderDiagram();
  }, [chart, idRef]);

  if (!chart) return null;

  return (
    <div className="mermaid-diagram-container">
      {error ? (
        <div className="mermaid-error">
          <p>{error}</p>
          <pre className="mermaid-raw">{chart}</pre>
        </div>
      ) : (
        <div ref={containerRef} className="mermaid-rendered" />
      )}
    </div>
  );
}
