import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { RunMetric } from '@/hooks/useAthleteRunMetrics';

const BRAND_COLORS = {
  orange: '#FF6B35',
  black: '#000000',
  lightOrange: '#FFB399',
};

interface ChartProps {
  data: RunMetric[];
}

const transformDataForLROverlay = (data: RunMetric[], metric: 'gct_ms' | 'flight_ms') => {
  const strideMap = new Map<number, { stride_num: number; left?: number; right?: number }>();
  
  data.forEach(row => {
    if (!strideMap.has(row.stride_num)) {
      strideMap.set(row.stride_num, { stride_num: row.stride_num });
    }
    const stride = strideMap.get(row.stride_num)!;
    stride[row.foot as 'left' | 'right'] = row[metric];
  });
  
  return Array.from(strideMap.values()).sort((a, b) => a.stride_num - b.stride_num);
};

const transformDataForStackedBar = (data: RunMetric[]) => {
  return data.map(row => ({
    stride_num: row.stride_num,
    foot: row.foot,
    label: `${row.stride_num}${row.foot === 'left' ? 'L' : 'R'}`,
    gct_ms: row.gct_ms,
    flight_ms: row.flight_ms,
  })).sort((a, b) => a.stride_num - b.stride_num);
};

export const GroundContactTimeChart = ({ data }: ChartProps) => {
  const chartData = transformDataForLROverlay(data, 'gct_ms');
  
  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold mb-2">Ground Contact Time (GCT) - Left vs Right Foot</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
          <XAxis dataKey="stride_num" label={{ value: 'Stride Number', position: 'insideBottom', offset: -5 }} />
          <YAxis label={{ value: 'Time (milliseconds)', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="left" 
            stroke={BRAND_COLORS.orange}
            strokeWidth={2}
            name="Left Foot"
            dot={{ fill: BRAND_COLORS.orange }}
          />
          <Line 
            type="monotone" 
            dataKey="right" 
            stroke={BRAND_COLORS.black}
            strokeWidth={2}
            name="Right Foot"
            dot={{ fill: BRAND_COLORS.black }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export const FlightTimeChart = ({ data }: ChartProps) => {
  const chartData = transformDataForLROverlay(data, 'flight_ms');
  
  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold mb-2">Flight Time (FT) - Left vs Right Foot</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
          <XAxis dataKey="stride_num" label={{ value: 'Stride Number', position: 'insideBottom', offset: -5 }} />
          <YAxis label={{ value: 'Time (milliseconds)', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="left" 
            stroke={BRAND_COLORS.orange}
            strokeWidth={2}
            name="Left Foot"
            dot={{ fill: BRAND_COLORS.orange }}
          />
          <Line 
            type="monotone" 
            dataKey="right" 
            stroke={BRAND_COLORS.black}
            strokeWidth={2}
            name="Right Foot"
            dot={{ fill: BRAND_COLORS.black }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export const StepTimeChart = ({ data }: ChartProps) => {
  const chartData = transformDataForStackedBar(data);
  
  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold mb-2">Step Time - Ground Contact + Flight Time (Stacked)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
          <XAxis dataKey="label" label={{ value: 'Step (Stride Number + Foot)', position: 'insideBottom', offset: -5 }} />
          <YAxis label={{ value: 'Time (milliseconds)', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          <Bar dataKey="gct_ms" stackId="a" fill={BRAND_COLORS.orange} name="Ground Contact" />
          <Bar dataKey="flight_ms" stackId="a" fill={BRAND_COLORS.lightOrange} name="Flight" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};