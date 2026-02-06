/**
 * Risk Matrix Chart Component
 *
 * Renders a 5x5 heatmap grid showing risks positioned by likelihood and impact.
 * Color-coded by severity: green (low), yellow (medium), orange (high), red (critical).
 */

import { useMemo } from 'react';

export interface RiskMatrixItem {
  id: string;
  name: string;
  description: string;
  likelihood: number; // 1-5
  impact: number; // 1-5
  risk_score: number; // likelihood * impact
  category: string;
  mitigation: string;
  owner?: string;
}

export interface RiskMatrixData {
  risks: RiskMatrixItem[];
  high_priority_count: number;
  overall_risk_level: string;
}

function getRiskColor(score: number): string {
  if (score <= 4) return '#22c55e'; // Green - Low
  if (score <= 9) return '#eab308'; // Yellow - Medium
  if (score <= 15) return '#f97316'; // Orange - High
  return '#ef4444'; // Red - Critical
}

export function RiskMatrixChart({ data }: { data: RiskMatrixData }) {
  // Group risks by grid cell
  const riskGrid = useMemo(() => {
    const grid: Map<string, RiskMatrixItem[]> = new Map();

    data.risks.forEach((risk) => {
      const key = `${risk.likelihood}-${risk.impact}`;
      if (!grid.has(key)) {
        grid.set(key, []);
      }
      grid.get(key)!.push(risk);
    });

    return grid;
  }, [data.risks]);

  if (!data?.risks || data.risks.length === 0) {
    return (
      <div className="chart-empty">
        <p>No risk data available</p>
      </div>
    );
  }

  return (
    <div className="risk-matrix-chart">
      {/* Matrix Grid */}
      <div className="matrix-container">
        {/* Y-axis label */}
        <div className="y-axis-label">
          <span>Impact</span>
        </div>

        {/* Y-axis ticks */}
        <div className="y-axis-ticks">
          {[5, 4, 3, 2, 1].map((val) => (
            <div key={val} className="tick">{val}</div>
          ))}
        </div>

        {/* Grid */}
        <div className="matrix-grid">
          {[5, 4, 3, 2, 1].map((impact) => (
            <div key={impact} className="matrix-row">
              {[1, 2, 3, 4, 5].map((likelihood) => {
                const cellKey = `${likelihood}-${impact}`;
                const cellRisks = riskGrid.get(cellKey) || [];
                const cellScore = likelihood * impact;
                const bgColor = getRiskColor(cellScore);

                return (
                  <div
                    key={cellKey}
                    className="matrix-cell"
                    style={{
                      backgroundColor: `${bgColor}20`,
                      borderColor: bgColor,
                    }}
                  >
                    {cellRisks.map((risk, idx) => (
                      <div
                        key={risk.id}
                        className="risk-dot"
                        style={{ backgroundColor: getRiskColor(risk.risk_score) }}
                        title={`${risk.name}: ${risk.description}`}
                      >
                        {cellRisks.length === 1 ? risk.name.substring(0, 3).toUpperCase() : idx + 1}
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          ))}
        </div>

        {/* X-axis ticks */}
        <div className="x-axis-ticks">
          {[1, 2, 3, 4, 5].map((val) => (
            <div key={val} className="tick">{val}</div>
          ))}
        </div>

        {/* X-axis label */}
        <div className="x-axis-label">
          <span>Likelihood</span>
        </div>
      </div>

      {/* Legend */}
      <div className="matrix-legend">
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#22c55e' }} />
          <span>Low (1-4)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#eab308' }} />
          <span>Medium (5-9)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#f97316' }} />
          <span>High (10-15)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#ef4444' }} />
          <span>Critical (16-25)</span>
        </div>
      </div>

      {/* Risk List */}
      <div className="risk-list">
        <h4>Identified Risks ({data.risks.length})</h4>
        <div className="risk-items">
          {data.risks
            .sort((a, b) => b.risk_score - a.risk_score)
            .map((risk) => (
              <div key={risk.id} className="risk-item">
                <div className="risk-header">
                  <span
                    className="risk-indicator"
                    style={{ backgroundColor: getRiskColor(risk.risk_score) }}
                  />
                  <span className="risk-name">{risk.name}</span>
                  <span className="risk-score">Score: {risk.risk_score}</span>
                </div>
                <p className="risk-description">{risk.description}</p>
                <p className="risk-mitigation">
                  <strong>Mitigation:</strong> {risk.mitigation}
                </p>
              </div>
            ))}
        </div>
      </div>

      {/* Summary */}
      <div className="matrix-summary">
        <div className="summary-stat">
          <span className="stat-label">Overall Risk Level</span>
          <span
            className="stat-value"
            style={{
              color: data.overall_risk_level === 'critical' ? '#ef4444' :
                     data.overall_risk_level === 'high' ? '#f97316' :
                     data.overall_risk_level === 'medium' ? '#eab308' : '#22c55e'
            }}
          >
            {data.overall_risk_level.toUpperCase()}
          </span>
        </div>
        <div className="summary-stat">
          <span className="stat-label">High Priority Risks</span>
          <span className="stat-value">{data.high_priority_count}</span>
        </div>
      </div>
    </div>
  );
}

export default RiskMatrixChart;
