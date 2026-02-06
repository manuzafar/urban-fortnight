/**
 * Financial Projection Chart Component
 *
 * Renders an area chart showing revenue, costs, and profit over time.
 * Highlights the break-even point and includes user growth on a secondary axis.
 */

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  CartesianGrid,
} from 'recharts';

export interface MonthlyProjection {
  month: number;
  revenue: number;
  costs: number;
  profit: number;
  users: number;
  mrr: number;
  arr?: number;
}

export interface FinancialProjectionData {
  monthly_data: MonthlyProjection[];
  break_even_month: number | null;
  year_1_revenue: string;
  year_1_costs: string;
  year_1_profit: string;
  year_3_revenue?: string;
  assumptions?: string[];
  sensitivity_notes?: string;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    name: string;
    value: number;
    color: string;
  }>;
  label?: string;
}

function formatCurrency(value: number): string {
  if (value >= 1000000) {
    return `$${(value / 1000000).toFixed(1)}M`;
  } else if (value >= 1000) {
    return `$${(value / 1000).toFixed(0)}k`;
  } else if (value < 0) {
    return `-$${Math.abs(value).toLocaleString()}`;
  }
  return `$${value.toLocaleString()}`;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="chart-tooltip">
      <div className="tooltip-header">
        <strong>Month {label}</strong>
      </div>
      <div className="tooltip-metrics">
        {payload.map((entry) => (
          <div key={entry.name} className="tooltip-metric" style={{ color: entry.color }}>
            <span className="metric-name">{entry.name}:</span>
            <span className="metric-value">
              {entry.name === 'Users' ? entry.value.toLocaleString() : formatCurrency(entry.value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function FinancialProjectionChart({ data }: { data: FinancialProjectionData }) {
  if (!data?.monthly_data || data.monthly_data.length === 0) {
    return (
      <div className="chart-empty">
        <p>No financial projection data available</p>
      </div>
    );
  }

  // Colors
  const REVENUE_COLOR = '#22c55e';
  const COSTS_COLOR = '#ef4444';
  const PROFIT_COLOR = '#3b82f6';

  return (
    <div className="financial-projection-chart">
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={data.monthly_data} margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />

          <XAxis
            dataKey="month"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#d1d5db' }}
            tickFormatter={(value) => `M${value}`}
          />

          <YAxis
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#d1d5db' }}
            tickFormatter={(value) => formatCurrency(value)}
          />

          <Tooltip content={<CustomTooltip />} />

          <Legend
            verticalAlign="top"
            height={36}
            wrapperStyle={{ paddingBottom: '10px' }}
          />

          {/* Break-even reference line */}
          {data.break_even_month && (
            <ReferenceLine
              x={data.break_even_month}
              stroke="#8b5cf6"
              strokeDasharray="5 5"
              strokeWidth={2}
              label={{
                value: 'Break-even',
                position: 'top',
                fill: '#8b5cf6',
                fontSize: 12,
              }}
            />
          )}

          {/* Zero line for profit */}
          <ReferenceLine y={0} stroke="#9ca3af" strokeWidth={1} />

          <Area
            type="monotone"
            dataKey="revenue"
            name="Revenue"
            stroke={REVENUE_COLOR}
            fill={REVENUE_COLOR}
            fillOpacity={0.2}
            strokeWidth={2}
          />

          <Area
            type="monotone"
            dataKey="costs"
            name="Costs"
            stroke={COSTS_COLOR}
            fill={COSTS_COLOR}
            fillOpacity={0.2}
            strokeWidth={2}
          />

          <Area
            type="monotone"
            dataKey="profit"
            name="Profit"
            stroke={PROFIT_COLOR}
            fill={PROFIT_COLOR}
            fillOpacity={0.3}
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Summary Stats */}
      <div className="chart-summary-stats">
        <div className="stat-card">
          <span className="stat-label">Year 1 Revenue</span>
          <span className="stat-value revenue">{data.year_1_revenue}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Year 1 Costs</span>
          <span className="stat-value costs">{data.year_1_costs}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Year 1 Profit</span>
          <span className="stat-value profit">{data.year_1_profit}</span>
        </div>
        {data.break_even_month && (
          <div className="stat-card">
            <span className="stat-label">Break-even</span>
            <span className="stat-value breakeven">Month {data.break_even_month}</span>
          </div>
        )}
        {data.year_3_revenue && (
          <div className="stat-card">
            <span className="stat-label">Year 3 Revenue</span>
            <span className="stat-value year3">{data.year_3_revenue}</span>
          </div>
        )}
      </div>

      {/* Assumptions */}
      {data.assumptions && data.assumptions.length > 0 && (
        <div className="chart-assumptions">
          <strong>Key Assumptions:</strong>
          <ul>
            {data.assumptions.map((assumption, index) => (
              <li key={index}>{assumption}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Sensitivity Notes */}
      {data.sensitivity_notes && (
        <div className="chart-sensitivity">
          <strong>Sensitivity:</strong> {data.sensitivity_notes}
        </div>
      )}
    </div>
  );
}

export default FinancialProjectionChart;
