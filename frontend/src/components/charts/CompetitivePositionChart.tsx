/**
 * Competitive Position Chart Component
 *
 * Renders a scatter plot showing competitor positions on a 2D strategic map.
 * Highlights the target product with a different color and larger marker.
 */

import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from 'recharts';

export interface CompetitorPosition {
  name: string;
  x_score: number;
  y_score: number;
  description: string;
  market_share?: string | null;
  funding?: string | null;
  is_target_product: boolean;
}

export interface CompetitivePositioningData {
  competitors: CompetitorPosition[];
  x_axis_label: string;
  y_axis_label: string;
  x_axis_low?: string;
  x_axis_high?: string;
  y_axis_low?: string;
  y_axis_high?: string;
  insight?: string;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: CompetitorPosition;
  }>;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0].payload;

  return (
    <div className="chart-tooltip">
      <div className="tooltip-header">
        <strong>{data.name}</strong>
        {data.is_target_product && <span className="target-badge">Our Product</span>}
      </div>
      <p className="tooltip-description">{data.description}</p>
      <div className="tooltip-scores">
        <span>Position: ({data.x_score.toFixed(1)}, {data.y_score.toFixed(1)})</span>
      </div>
      {data.market_share && (
        <div className="tooltip-detail">Market Share: {data.market_share}</div>
      )}
      {data.funding && (
        <div className="tooltip-detail">Funding: {data.funding}</div>
      )}
    </div>
  );
}

export function CompetitivePositionChart({ data }: { data: CompetitivePositioningData }) {
  if (!data?.competitors || data.competitors.length === 0) {
    return (
      <div className="chart-empty">
        <p>No competitive positioning data available</p>
      </div>
    );
  }

  // Colors for competitors and target product
  const COMPETITOR_COLOR = '#6366f1';
  const TARGET_COLOR = '#22c55e';

  return (
    <div className="competitive-position-chart">
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 20, right: 40, bottom: 60, left: 60 }}>
          {/* Grid lines at midpoint */}
          <ReferenceLine x={5} stroke="#e5e7eb" strokeDasharray="3 3" />
          <ReferenceLine y={5} stroke="#e5e7eb" strokeDasharray="3 3" />

          <XAxis
            type="number"
            dataKey="x_score"
            domain={[0, 10]}
            tickCount={6}
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <YAxis
            type="number"
            dataKey="y_score"
            domain={[0, 10]}
            tickCount={6}
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#d1d5db' }}
          />

          <Tooltip content={<CustomTooltip />} />

          <Scatter
            data={data.competitors}
            fill={COMPETITOR_COLOR}
          >
            {data.competitors.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.is_target_product ? TARGET_COLOR : COMPETITOR_COLOR}
                stroke={entry.is_target_product ? '#16a34a' : '#4f46e5'}
                strokeWidth={2}
                r={entry.is_target_product ? 12 : 8}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>

      {/* Axis labels */}
      <div className="chart-axis-labels">
        <div className="x-axis-label">
          <span className="axis-low">{data.x_axis_low || 'Low'}</span>
          <span className="axis-name">{data.x_axis_label}</span>
          <span className="axis-high">{data.x_axis_high || 'High'}</span>
        </div>
        <div className="y-axis-label">
          <span className="axis-low">{data.y_axis_low || 'Low'}</span>
          <span className="axis-name">{data.y_axis_label}</span>
          <span className="axis-high">{data.y_axis_high || 'High'}</span>
        </div>
      </div>

      {/* Legend */}
      <div className="chart-legend">
        <div className="legend-item">
          <span className="legend-dot competitor" />
          <span>Competitors</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot target" />
          <span>Our Product</span>
        </div>
      </div>

      {/* Insight */}
      {data.insight && (
        <div className="chart-insight">
          <strong>Key Insight:</strong> {data.insight}
        </div>
      )}
    </div>
  );
}

export default CompetitivePositionChart;
