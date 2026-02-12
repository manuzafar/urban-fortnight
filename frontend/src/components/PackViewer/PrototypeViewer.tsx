/**
 * PrototypeViewer - renders the interactive prototype in a polished iframe.
 */

import { useMemo, useState } from 'react';

interface PrototypeViewerProps {
  prototype: {
    prototype_name?: string;
    primary_persona?: string;
    key_user_story?: string;
    react_component_code?: string;
    react_code?: string; // Backend may use this instead
    css_code?: string;
    color_palette?: {
      primary: string;
      secondary: string;
      accent: string;
      background: string;
      text: string;
    };
    interactivity_notes?: string[];
    demo_scenario?: string;
  };
  className?: string;
}

export function PrototypeViewer({ prototype, className = '' }: PrototypeViewerProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Support both field names
  const reactCode = prototype?.react_component_code || prototype?.react_code;

  if (!reactCode) {
    return (
      <div className={`p-8 text-center text-gray-500 ${className}`}>
        No prototype available
      </div>
    );
  }

  const iframeSrc = useMemo(() => {
    // Preprocess the code for browser compatibility
    let processedCode = reactCode;

    // Remove ALL import statements (react, lucide-react, etc.)
    processedCode = processedCode.replace(/import\s+.*?from\s+['"][^'"]+['"];?\s*\n?/g, '');
    processedCode = processedCode.replace(/import\s+['"][^'"]+['"];?\s*\n?/g, '');

    // Remove export statements but keep the function definition
    // e.g., "export default function Foo" -> "function Foo"
    processedCode = processedCode.replace(/export\s+default\s+function/g, 'function');
    processedCode = processedCode.replace(/export\s+default\s+\w+;?\s*\n?/g, '');
    processedCode = processedCode.replace(/export\s+\{[^}]+\};?\s*\n?/g, '');

    // FIX: LLM sometimes generates broken syntax like "ComponentName() {" without "function"
    // This regex finds patterns like "ComponentName() {" at the start of a line (or after whitespace)
    // and adds "function " before it. Only matches PascalCase names (components).
    processedCode = processedCode.replace(
      /^(\s*)([A-Z][a-zA-Z0-9]*)\s*\(\s*\)\s*\{/gm,
      '$1function $2() {'
    );

    // Also handle "const ComponentName = () => {" that might be malformed
    // e.g., "ComponentName = () => {" without "const"
    processedCode = processedCode.replace(
      /^(\s*)([A-Z][a-zA-Z0-9]*)\s*=\s*\(\s*\)\s*=>\s*\{/gm,
      '$1const $2 = () => {'
    );

    // Replace destructured hooks with React.* versions
    processedCode = processedCode.replace(/\buseState\b/g, 'React.useState');
    processedCode = processedCode.replace(/\buseEffect\b/g, 'React.useEffect');
    processedCode = processedCode.replace(/\buseRef\b/g, 'React.useRef');
    processedCode = processedCode.replace(/\buseMemo\b/g, 'React.useMemo');
    processedCode = processedCode.replace(/\buseCallback\b/g, 'React.useCallback');

    // Extract component name
    const funcMatch = processedCode.match(/function\s+([A-Z][a-zA-Z0-9]*)/);
    const constMatch = processedCode.match(/const\s+([A-Z][a-zA-Z0-9]*)\s*=/);
    const componentName = funcMatch?.[1] || constMatch?.[1] || 'AppPrototype';

    // Escape for template literal
    const escapedCode = processedCode
      .replace(/\\/g, '\\\\')
      .replace(/`/g, '\\`')
      .replace(/\$\{/g, '\\${');

    const escapedCss = (prototype.css_code || '')
      .replace(/\\/g, '\\\\')
      .replace(/`/g, '\\`')
      .replace(/\$\{/g, '\\${');

    const html = `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
          <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
          <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
          <script src="https://cdn.tailwindcss.com"></script>
          <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
          <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
          <style>
            body { margin: 0; background: white; min-height: 100vh; font-family: 'Inter', system-ui, sans-serif; }
            .error { color: #991b1b; background: #fee2e2; padding: 20px; border-radius: 8px; margin: 20px; }
            ${escapedCss}
          </style>
          <script>
            // Create React components for Lucide icons
            window.createLucideIcon = function(iconName) {
              return function LucideIcon(props) {
                const ref = React.useRef(null);
                React.useEffect(() => {
                  if (ref.current && window.lucide && window.lucide.icons[iconName]) {
                    const [, attrs, children] = window.lucide.icons[iconName];
                    ref.current.innerHTML = '';
                    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                    Object.entries({...attrs, width: props.size || 24, height: props.size || 24, stroke: props.color || 'currentColor', ...props}).forEach(([k, v]) => {
                      if (k !== 'size' && k !== 'children' && typeof v !== 'object') svg.setAttribute(k === 'strokeWidth' ? 'stroke-width' : k, v);
                    });
                    svg.innerHTML = children.map(([tag, attrs]) => {
                      const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
                      Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
                      return el.outerHTML;
                    }).join('');
                    ref.current.appendChild(svg);
                  }
                }, []);
                return React.createElement('span', { ref: ref, className: props.className, style: { display: 'inline-flex', verticalAlign: 'middle' } });
              };
            };
            // Common Lucide icons used in prototypes
            var iconNames = ['search','bell','settings','plus','filter','menu','x','check','chevron-right','chevron-left','chevron-down','chevron-up','arrow-right','arrow-left','arrow-up','arrow-down','home','user','users','mail','phone','calendar','clock','star','heart','trash','trash-2','edit','edit-2','edit-3','eye','eye-off','download','upload','share','share-2','copy','link','external-link','info','alert-triangle','alert-circle','check-circle','x-circle','plus-circle','minus-circle','help-circle','shopping-cart','shopping-bag','shopping-basket','credit-card','dollar-sign','percent','tag','box','package','truck','map-pin','navigation','navigation-2','globe','sun','moon','cloud','image','camera','file','file-text','folder','database','server','code','terminal','git-branch','layout-grid','layout-list','list','grid','bar-chart','bar-chart-2','pie-chart','trending-up','trending-down','activity','zap','shield','lock','unlock','key','log-in','log-out','refresh-cw','rotate-cw','save','send','message-circle','message-square','more-horizontal','more-vertical','sliders','toggle-left','toggle-right'];
            iconNames.forEach(function(name) {
              var camelName = name.split('-').map(function(s, i) { return i === 0 ? s : s.charAt(0).toUpperCase() + s.slice(1); }).join('');
              var pascalName = camelName.charAt(0).toUpperCase() + camelName.slice(1);
              window[pascalName] = window.createLucideIcon(name);
            });
          </script>
        </head>
        <body>
          <div id="root"></div>
          <script type="text/babel">
            try {
              ${escapedCode}
              const root = ReactDOM.createRoot(document.getElementById('root'));
              root.render(React.createElement(${componentName}));
            } catch (e) {
              document.getElementById('root').innerHTML =
                '<div class="error"><strong>Prototype Render Error:</strong> ' + e.message + '</div>';
              console.error('Prototype error:', e);
            }
          </script>
        </body>
      </html>
    `;

    return `data:text/html;charset=utf-8,${encodeURIComponent(html)}`;
  }, [reactCode, prototype.css_code]);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-lg">{prototype.prototype_name || 'Interactive Prototype'}</h3>
          {prototype.primary_persona && (
            <p className="text-gray-600 text-sm">
              For: {prototype.primary_persona}
            </p>
          )}
        </div>
        <button
          onClick={() => setIsFullscreen(!isFullscreen)}
          className="px-3 py-1.5 text-sm border rounded-lg hover:bg-gray-50 transition-colors"
        >
          {isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
        </button>
      </div>

      {/* Key user story */}
      {prototype.key_user_story && (
        <div className="bg-blue-50 border border-blue-100 rounded-lg p-3">
          <p className="text-sm text-blue-800">
            <span className="font-medium">Demonstrates: </span>
            {prototype.key_user_story}
          </p>
        </div>
      )}

      {/* Prototype iframe */}
      <div
        className={`
          border rounded-lg overflow-hidden bg-white shadow-lg transition-all duration-300
          ${isFullscreen ? 'fixed inset-4 z-50' : ''}
        `}
      >
        {/* Browser chrome */}
        <div className="bg-gray-100 px-3 py-2 flex items-center gap-3 border-b">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-400" />
            <div className="w-3 h-3 rounded-full bg-yellow-400" />
            <div className="w-3 h-3 rounded-full bg-green-400" />
          </div>
          <div className="flex-1 bg-white rounded px-3 py-1 text-xs text-gray-500 text-center">
            {(prototype.prototype_name || 'prototype').toLowerCase().replace(/\s+/g, '-')}.app
          </div>
        </div>

        <iframe
          src={iframeSrc}
          className={`w-full border-0 ${isFullscreen ? 'h-[calc(100%-40px)]' : 'h-[600px]'}`}
          sandbox="allow-scripts"
          title="Interactive prototype"
        />
      </div>

      {/* Fullscreen overlay */}
      {isFullscreen && (
        <div
          className="fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsFullscreen(false)}
        />
      )}

      {/* Color palette */}
      {prototype.color_palette && (
        <div className="flex gap-2">
          {Object.entries(prototype.color_palette).map(([name, color]) => (
            <div key={name} className="flex items-center gap-1 text-sm">
              <div
                className="w-6 h-6 rounded border"
                style={{ backgroundColor: color.startsWith('#') ? color : undefined }}
              />
              <span className="text-gray-600 capitalize">{name}</span>
            </div>
          ))}
        </div>
      )}

      {/* Demo scenario */}
      {prototype.demo_scenario && (
        <div className="border-t pt-4">
          <h4 className="font-medium mb-2">Demo Scenario</h4>
          <p className="text-gray-600 text-sm whitespace-pre-line">
            {prototype.demo_scenario}
          </p>
        </div>
      )}

      {/* Interactivity notes */}
      {prototype.interactivity_notes && prototype.interactivity_notes.length > 0 && (
        <div className="border-t pt-4">
          <h4 className="font-medium mb-2">Interactive Elements</h4>
          <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
            {prototype.interactivity_notes?.map((note, i) => (
              <li key={i}>{note}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default PrototypeViewer;
