/**
 * WireframeViewer - renders wireframe screens in sandboxed iframes.
 */

import { useState, useMemo } from 'react';

interface WireframeScreen {
  screen_id: string;
  screen_name: string;
  purpose: string;
  user_stories_covered: string[];
  key_components: string[];
  navigation_to: string[];
  react_code: string;
}

interface WireframeViewerProps {
  wireframes: {
    screens: WireframeScreen[];
    user_flow_description?: string;
    user_flow_mermaid?: string;
    design_system_notes?: string[];
  };
  className?: string;
}

export function WireframeViewer({ wireframes, className = '' }: WireframeViewerProps) {
  const [activeScreen, setActiveScreen] = useState(0);

  if (!wireframes?.screens?.length) {
    return (
      <div className={`p-8 text-center text-gray-500 ${className}`}>
        No wireframes available
      </div>
    );
  }

  const screens = wireframes.screens;
  const currentScreen = screens[activeScreen];

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Screen tabs */}
      <div className="flex gap-2 flex-wrap">
        {screens.map((screen, index) => (
          <button
            key={screen.screen_id}
            onClick={() => setActiveScreen(index)}
            className={`
              px-3 py-1.5 text-sm rounded-lg border transition-colors
              ${activeScreen === index
                ? 'bg-gray-900 text-white border-gray-900'
                : 'bg-white text-gray-700 border-gray-300 hover:border-gray-400'
              }
            `}
          >
            {screen.screen_id}: {screen.screen_name}
          </button>
        ))}
      </div>

      {/* Screen info */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-medium text-lg">{currentScreen.screen_name}</h3>
        <p className="text-gray-600 text-sm mt-1">{currentScreen.purpose}</p>

        {currentScreen.user_stories_covered?.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {currentScreen.user_stories_covered.map((story) => (
              <span
                key={story}
                className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded"
              >
                {story}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Wireframe preview - key ensures React creates new iframe when switching screens */}
      <WireframePreview key={currentScreen.screen_id} code={currentScreen.react_code} />

      {/* Navigation links */}
      {currentScreen.navigation_to?.length > 0 && (
        <div className="text-sm text-gray-600">
          <span className="font-medium">Navigates to: </span>
          {currentScreen.navigation_to.map((target, i) => {
            const targetIndex = screens.findIndex((s) => s.screen_id === target);
            return (
              <span key={target}>
                {i > 0 && ', '}
                <button
                  onClick={() => targetIndex >= 0 && setActiveScreen(targetIndex)}
                  className="text-blue-600 hover:underline"
                >
                  {target}
                </button>
              </span>
            );
          })}
        </div>
      )}

      {/* User flow description */}
      {wireframes.user_flow_description && (
        <div className="border-t pt-4 mt-4">
          <h4 className="font-medium mb-2">User Flow</h4>
          <p className="text-gray-600 text-sm">{wireframes.user_flow_description}</p>
        </div>
      )}
    </div>
  );
}

/**
 * Preprocesses React code for browser execution.
 * - Removes ALL import/export statements
 * - Fixes broken function declarations (e.g., "ComponentName() {" -> "function ComponentName() {")
 * - Extracts component name
 * - Replaces React hooks with React.* versions
 */
function preprocessCode(code: string): { processedCode: string; componentName: string } {
  let processed = code;

  // Remove ALL import statements (react, lucide-react, etc.)
  processed = processed.replace(/import\s+.*?from\s+['"][^'"]+['"];?\s*\n?/g, '');
  processed = processed.replace(/import\s+['"][^'"]+['"];?\s*\n?/g, '');

  // Remove export statements but keep the function definition
  // e.g., "export default function Foo" -> "function Foo"
  processed = processed.replace(/export\s+default\s+function/g, 'function');
  processed = processed.replace(/export\s+default\s+\w+;?\s*\n?/g, '');
  processed = processed.replace(/export\s+\{[^}]+\};?\s*\n?/g, '');

  // FIX: LLM sometimes generates broken syntax like "ComponentName() {" without "function"
  // This regex finds patterns like "ComponentName() {" at the start of a line (or after whitespace)
  // and adds "function " before it. Only matches PascalCase names (components).
  processed = processed.replace(
    /^(\s*)([A-Z][a-zA-Z0-9]*)\s*\(\s*\)\s*\{/gm,
    '$1function $2() {'
  );

  // Also handle "const ComponentName = () => {" that might be malformed
  // e.g., "ComponentName = () => {" without "const"
  processed = processed.replace(
    /^(\s*)([A-Z][a-zA-Z0-9]*)\s*=\s*\(\s*\)\s*=>\s*\{/gm,
    '$1const $2 = () => {'
  );

  // Replace destructured hooks with React.* versions
  processed = processed.replace(/\buseState\b/g, 'React.useState');
  processed = processed.replace(/\buseEffect\b/g, 'React.useEffect');
  processed = processed.replace(/\buseRef\b/g, 'React.useRef');
  processed = processed.replace(/\buseMemo\b/g, 'React.useMemo');
  processed = processed.replace(/\buseCallback\b/g, 'React.useCallback');

  // Extract component name
  const funcMatch = processed.match(/function\s+([A-Z][a-zA-Z0-9]*)/);
  const constMatch = processed.match(/const\s+([A-Z][a-zA-Z0-9]*)\s*=/);
  const componentName = funcMatch?.[1] || constMatch?.[1] || 'App';

  return { processedCode: processed, componentName };
}

/**
 * Escapes code for embedding in template literal.
 */
function escapeForTemplateLiteral(code: string): string {
  return code
    .replace(/\\/g, '\\\\')
    .replace(/`/g, '\\`')
    .replace(/\$\{/g, '\\${');
}

/**
 * WireframePreview - renders React code in a sandboxed iframe using Babel.
 */
function WireframePreview({ code }: { code: string }) {
  const iframeSrc = useMemo(() => {
    const { processedCode, componentName } = preprocessCode(code);
    const escapedCode = escapeForTemplateLiteral(processedCode);

    // Create HTML document with Babel for JSX transformation
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
          <style>
            body { margin: 0; padding: 16px; background: #f9fafb; font-family: system-ui, sans-serif; }
            .error { color: #991b1b; background: #fee2e2; padding: 16px; border-radius: 8px; }
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
            // Common Lucide icons used in wireframes (comprehensive list)
            var iconNames = ['search','bell','settings','plus','minus','filter','menu','x','check','chevron-right','chevron-left','chevron-down','chevron-up','arrow-right','arrow-left','arrow-up','arrow-down','home','user','users','user-plus','user-minus','user-check','mail','phone','calendar','clock','star','heart','trash','trash-2','edit','edit-2','edit-3','eye','eye-off','download','upload','share','share-2','copy','link','external-link','info','alert-triangle','alert-circle','check-circle','x-circle','plus-circle','minus-circle','help-circle','shopping-cart','shopping-bag','shopping-basket','credit-card','dollar-sign','percent','tag','tags','box','package','archive','truck','map','map-pin','navigation','navigation-2','globe','globe-2','sun','moon','cloud','cloud-rain','image','camera','video','file','file-text','file-plus','folder','folder-plus','database','server','hard-drive','cpu','code','terminal','git-branch','git-commit','git-merge','layout','layout-grid','layout-list','list','list-ordered','grid','columns','rows','bar-chart','bar-chart-2','bar-chart-3','bar-chart-4','pie-chart','line-chart','trending-up','trending-down','activity','zap','shield','shield-check','lock','unlock','key','log-in','log-out','refresh-cw','refresh-ccw','rotate-cw','rotate-ccw','save','send','message-circle','message-square','messages-square','more-horizontal','more-vertical','sliders','sliders-horizontal','toggle-left','toggle-right','wifi','wifi-off','bluetooth','battery','battery-charging','power','play','pause','stop','skip-forward','skip-back','volume','volume-1','volume-2','volume-x','mic','mic-off','headphones','monitor','smartphone','tablet','laptop','printer','scan','qr-code','barcode','receipt','clipboard','clipboard-list','clipboard-check','notepad','book','book-open','bookmark','graduation-cap','briefcase','building','building-2','store','warehouse','factory','landmark','award','trophy','medal','target','flag','rocket','plane','car','bike','ship','anchor','compass','layers','maximize','minimize','maximize-2','minimize-2','expand','shrink','move','grip-vertical','grip-horizontal'];
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
                '<div class="error"><strong>Render Error:</strong> ' + e.message + '</div>';
              console.error('Wireframe error:', e);
            }
          </script>
        </body>
      </html>
    `;

    return `data:text/html;charset=utf-8,${encodeURIComponent(html)}`;
  }, [code]);

  if (!code) {
    return (
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center text-gray-500">
        No code available for this wireframe
      </div>
    );
  }

  return (
    <div className="border rounded-lg overflow-hidden bg-white">
      <div className="bg-gray-100 px-3 py-2 text-xs text-gray-600 flex items-center gap-2">
        <div className="flex gap-1">
          <div className="w-3 h-3 rounded-full bg-red-400" />
          <div className="w-3 h-3 rounded-full bg-yellow-400" />
          <div className="w-3 h-3 rounded-full bg-green-400" />
        </div>
        <span>Wireframe Preview</span>
      </div>
      <iframe
        src={iframeSrc}
        className="w-full h-96 border-0"
        sandbox="allow-scripts"
        title="Wireframe preview"
      />
    </div>
  );
}

export default WireframeViewer;
