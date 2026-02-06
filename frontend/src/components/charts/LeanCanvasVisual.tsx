/**
 * Lean Canvas Visual Component
 *
 * Renders a visual Lean Canvas layout matching the standard 9-section format.
 * Optimized for readability and presentation.
 */

export interface LeanCanvasData {
  problem?: string[];
  solution?: string[];
  key_metrics?: string[];
  unique_value_proposition?: string;
  unfair_advantage?: string;
  channels?: string[];
  customer_segments?: string[];
  cost_structure?: string[];
  revenue_streams?: string[];
}

interface CanvasSectionProps {
  title: string;
  items?: string[];
  text?: string;
  className?: string;
}

function CanvasSection({ title, items, text, className = '' }: CanvasSectionProps) {
  return (
    <div className={`canvas-section ${className}`}>
      <h4 className="section-title">{title}</h4>
      <div className="section-content">
        {text && <p className="section-text">{text}</p>}
        {items && items.length > 0 && (
          <ul className="section-list">
            {items.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        )}
        {!text && (!items || items.length === 0) && (
          <p className="section-empty">Not specified</p>
        )}
      </div>
    </div>
  );
}

export function LeanCanvasVisual({ data }: { data: LeanCanvasData }) {
  if (!data) {
    return (
      <div className="chart-empty">
        <p>No Lean Canvas data available</p>
      </div>
    );
  }

  return (
    <div className="lean-canvas-visual">
      <div className="canvas-grid">
        {/* Row 1: Problem, Solution, UVP, Unfair Advantage, Customer Segments */}
        <div className="canvas-row top-row">
          {/* Problem - spans 2 rows */}
          <div className="canvas-column problem-column">
            <CanvasSection
              title="Problem"
              items={data.problem}
              className="problem"
            />
          </div>

          {/* Solution */}
          <div className="canvas-column solution-column">
            <CanvasSection
              title="Solution"
              items={data.solution}
              className="solution"
            />
          </div>

          {/* UVP - spans 2 rows */}
          <div className="canvas-column uvp-column">
            <CanvasSection
              title="Unique Value Proposition"
              text={data.unique_value_proposition}
              className="uvp"
            />
          </div>

          {/* Unfair Advantage */}
          <div className="canvas-column advantage-column">
            <CanvasSection
              title="Unfair Advantage"
              text={data.unfair_advantage}
              className="advantage"
            />
          </div>

          {/* Customer Segments - spans 2 rows */}
          <div className="canvas-column segments-column">
            <CanvasSection
              title="Customer Segments"
              items={data.customer_segments}
              className="segments"
            />
          </div>
        </div>

        {/* Row 2: Key Metrics, Channels */}
        <div className="canvas-row middle-row">
          <div className="canvas-column metrics-column">
            <CanvasSection
              title="Key Metrics"
              items={data.key_metrics}
              className="metrics"
            />
          </div>

          <div className="canvas-column channels-column">
            <CanvasSection
              title="Channels"
              items={data.channels}
              className="channels"
            />
          </div>
        </div>

        {/* Row 3: Cost Structure, Revenue Streams */}
        <div className="canvas-row bottom-row">
          <div className="canvas-column cost-column">
            <CanvasSection
              title="Cost Structure"
              items={data.cost_structure}
              className="cost"
            />
          </div>

          <div className="canvas-column revenue-column">
            <CanvasSection
              title="Revenue Streams"
              items={data.revenue_streams}
              className="revenue"
            />
          </div>
        </div>
      </div>

      {/* Canvas Footer */}
      <div className="canvas-footer">
        <span className="canvas-label">Lean Canvas</span>
      </div>
    </div>
  );
}

export default LeanCanvasVisual;
